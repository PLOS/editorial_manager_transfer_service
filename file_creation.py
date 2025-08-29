"""
A list of functions handling file exports and imports.
"""
__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

import os
import uuid
import xml.etree.cElementTree as ETree
import zipfile
from collections.abc import Sequence
from typing import List

from django.core.exceptions import ObjectDoesNotExist

import plugins.editorial_manager_transfer_service.consts as consts
import plugins.editorial_manager_transfer_service.logger_messages as logger_messages
from core.models import File
from journal.models import Journal
from submission.models import Article
from utils import setting_handler
from utils.logger import get_logger

logger = get_logger(__name__)


def get_article_export_folders() -> str:
    """
    Gets the filepaths for the folders used for exporting articles.

    :return: A list of filepaths for the export folders.
    """
    if os.path.exists(consts.EXPORT_FILE_PATH):
        return consts.EXPORT_FILE_PATH
    else:
        return ""


class ExportFileCreation:
    """
    A class for managing the export file creation process.
    """

    def __init__(self, article_id: str):
        self.zip_filepath: str | None = None
        self.go_filepath: str | None = None
        self.in_error_state: bool = False
        self.__license_code: str | None = None
        self.__journal_code: str | None = None
        self.__submission_partner_code: str | None = None
        self.article_id: str | None = article_id.strip() if article_id else None
        self.article: Article | None = None
        self.journal: Journal | None = None
        self.export_folder: str | None = None

        # If no article ID, return an error.
        if not self.article_id or len(self.article_id) <= 0:
            logger.error(logger_messages.process_failed_no_article_id_provided())
            self.in_error_state = True
            return

        # Get the article based upon the given article ID.
        logger.info(logger_messages.process_fetching_article(article_id))
        try:
            self.article: Article = self.__fetch_article(article_id)
        except Article.DoesNotExist:
            logger.error(logger_messages.process_failed_fetching_article(article_id))
            self.in_error_state = True
            return

        # Attempt to get the journal.
        self.journal: Journal = self.article.journal
        if self.journal is None:
            logger.error(logger_messages.process_failed_fetching_journal(article_id))
            self.in_error_state = True
            return

        # Get the export folder.
        export_folders: str = get_article_export_folders()
        if len(export_folders) <= 0:
            logger.error(logger_messages.export_process_failed_no_export_folder())
            self.in_error_state = True
            return
        self.export_folder = export_folders

        # Start export process
        self.__create_export_file()

    def get_zip_filepath(self) -> str | None:
        """
        Gets the zip file path for the exported files.
        :return: The zip file path.
        """
        if self.zip_filepath is None:
            self.in_error_state = True
            return None
        else:
            return self.zip_filepath

    def get_go_filepath(self) -> str | None:
        """
        Gets the filepath for the go.xml file for exporting to Editorial Manager.
        :return: The filepath for the go.xml file or None, if the process failed.
        """
        if self.go_filepath is None:
            self.in_error_state = True
            return None
        else:
            return self.go_filepath

    def __create_export_file(self):
        """
        Creates the export file for
        """

        if not self.can_export():
            self.in_error_state = True
            return

        # TODO: Attempt to create the metadata file.
        # metadata_file: File | None = self.__create_metadata_file(self.article)
        # if metadata_file is None:
        #     logger.error(logger_messages.process_failed_fetching_metadata(self.article_id))
        #     self.in_error_state = True
        #     return

        # Attempt to fetch the article files.
        article_files: Sequence[File] = self.__fetch_article_files(self.article)
        if len(article_files) <= 0:
            logger.error(logger_messages.process_failed_fetching_article_files(self.article_id))
            self.in_error_state = True
            return

        prefix: str = "{0}_{1}".format(self.get_submission_partner_code(), uuid.uuid4())

        self.zip_filepath: str = os.path.join(self.export_folder, "{0}.zip".format(prefix))
        with zipfile.ZipFile(self.zip_filepath, "w") as zipf:
            # TODO: zipf.write(metadata_file.get_file_path(self.article))
            for article_file in article_files:
                zipf.write(article_file.get_file_path(self.article))
            filenames: Sequence[str] = zipf.namelist()
            zipf.close()

        # Remove the manuscript

        # TODO: Remove below and replace with 'self.__create_go_xml_file(metadata_file.uuid_filename, filenames, prefix)'
        self.__create_go_xml_file("fake name", filenames, prefix)

    def get_license_code(self) -> str:
        """
        Gets the license code for exporting files.
        :return: The license code or None, if the process failed.
        """
        if not self.__license_code:
            self.__license_code: str = self.get_setting(consts.PLUGIN_SETTINGS_LICENSE_CODE)
        return self.__license_code

    def get_journal_code(self) -> str:
        """
        Gets the journal code for exporting files.
        :return: The journal code or None, if the process failed.
        """
        if not self.__journal_code:
            self.__journal_code: str = self.get_setting(consts.PLUGIN_SETTINGS_JOURNAL_CODE)
        return self.__journal_code

    def get_submission_partner_code(self) -> str:
        """
        Gets the submission partner code for exporting files.
        :return: The submission partner code or None, if the process failed.
        """
        if not self.__submission_partner_code:
            self.__submission_partner_code: str = self.get_setting(consts.PLUGIN_SETTINGS_SUBMISSION_PARTNER_CODE)
        return self.__submission_partner_code

    def can_export(self) -> bool:
        """
        Checks if the export file can be created.
        :return: True if the export file can be created, False otherwise.
        """
        return (not self.in_error_state and
                self.article is not None and
                self.journal is not None and
                self.get_license_code() is not None and
                self.get_journal_code() is not None and
                self.get_submission_partner_code() is not None)

    def get_setting(self, setting_name: str) -> str:
        """
        Gets the setting for the given setting name.
        :param setting_name: The name of the setting to get the value for.
        :return: The value for the given setting or a blank string, if the process failed.
        """
        try:
            return setting_handler.get_setting(setting_group_name=consts.PLUGIN_SETTINGS_GROUP_NAME,
                                               setting_name=setting_name, journal=self.journal, ).processed_value
        except ObjectDoesNotExist:
            logger.error("Could not get the following setting, '{0}'".format(setting_name))
            self.in_error_state = True
            return ""

    def __create_go_xml_file(self, metadata_filename: str, article_filenames: Sequence[str], filename: str):
        """
        Creates the go xml file for the export process for Editorial Manager.
        :param metadata_filename: The name of the metadata file.
        :param article_filenames: The filenames of the article's associated files.
        :param filename: The name to use for the go.xml file (Must match the name of the zip file).
        """
        if not self.can_export():
            self.in_error_state = True
            return

        go: ETree.Element = ETree.Element(consts.GO_FILE_ELEMENT_TAG_GO)
        go.set(consts.GO_FILE_GO_ELEMENT_ATTRIBUTE_XMLNS_XSI_KEY, consts.GO_FILE_GO_ELEMENT_ATTRIBUTE_XMLNS_XSI_VALUE)
        go.set(consts.GO_FILE_GO_ELEMENT_ATTRIBUTE_SCHEMA_LOCATION_KEY,
               consts.GO_FILE_GO_ELEMENT_ATTRIBUTE_SCHEMA_LOCATION_VALUE)

        # Format the header.
        header: ETree.Element = ETree.SubElement(go, consts.GO_FILE_ELEMENT_TAG_HEADER)
        version: ETree.Element = ETree.SubElement(header, consts.GO_FILE_ELEMENT_TAG_VERSION)
        version.set(consts.GO_FILE_VERSION_ELEMENT_ATTRIBUTE_NUMBER_KEY,
                    consts.GO_FILE_VERSION_ELEMENT_ATTRIBUTE_NUMBER_VALUE)
        journal: ETree.Element = ETree.SubElement(header, consts.GO_FILE_ELEMENT_TAG_JOURNAL)
        journal.set(consts.GO_FILE_JOURNAL_ELEMENT_ATTRIBUTE_CODE_KEY, self.get_license_code())
        import_type: ETree.Element = ETree.SubElement(header, consts.GO_FILE_ELEMENT_TAG_IMPORT_TYPE)
        import_type.set(consts.GO_FILE_IMPORT_TYPE_ELEMENT_ATTRIBUTE_ID_KEY,
                        consts.GO_FILE_IMPORT_TYPE_ELEMENT_ATTRIBUTE_ID_VALUE)
        parameters: ETree.Element = ETree.SubElement(header, consts.GO_FILE_ELEMENT_TAG_PARAMETERS)
        parameter: ETree.Element = ETree.SubElement(parameters, consts.GO_FILE_ELEMENT_TAG_PARAMETER)
        parameter.set(consts.GO_FILE_ATTRIBUTE_ELEMENT_NAME_KEY, consts.GO_FILE_PARAMETER_ELEMENT_NAME_VALUE)
        parameter.set(consts.GO_FILE_PARAMETER_ELEMENT_VALUE_KEY,
                      "{0}_{1}".format(self.get_submission_partner_code(), self.get_license_code()))

        # Begin the filegroup.
        filegroup: ETree.Element = ETree.SubElement(go, consts.GO_FILE_ELEMENT_TAG_FILEGROUP)

        # Create the archive and metadata files.
        archive_file: ETree.Element = ETree.SubElement(filegroup, consts.GO_FILE_ELEMENT_TAG_ARCHIVE_FILE)
        archive_file.set(consts.GO_FILE_ATTRIBUTE_ELEMENT_NAME_KEY, "{0}.zip".format(filename))
        metadata_file: ETree.Element = ETree.SubElement(filegroup, consts.GO_FILE_ELEMENT_TAG_METADATA_FILE)
        metadata_file.set(consts.GO_FILE_ATTRIBUTE_ELEMENT_NAME_KEY, metadata_filename)

        for article_filename in article_filenames:
            file_tree = ETree.SubElement(filegroup, consts.GO_FILE_ELEMENT_TAG_FILE)
            file_tree.set(consts.GO_FILE_ATTRIBUTE_ELEMENT_NAME_KEY, article_filename)

        tree = ETree.ElementTree(go)
        self.go_filepath = os.path.join(self.export_folder, "{0}.go.xml".format(filename))
        tree.write(self.go_filepath)

    def __create_metadata_file(self, article: Article) -> File | None:
        """
        Creates the metadata file based on the given article.
        :param article: The article to convert to JATS.
        :return:
        """
        pass

    @staticmethod
    def __fetch_article(article_id: str) -> Article:
        """
        Gets the article object for the given article ID.
        :param article_id: The ID of the article.
        :return: The article object with the given article ID.
        """
        return Article.get_article(article_id)

    @staticmethod
    def __fetch_article_files(article: Article) -> List[File]:
        """
        Fetches the manuscript (or content or body) of an article alongside any other files associated with it.
        :param article: The article to fetch the manuscript files for.
        :return: A list of all files related to the article.
        """

        files: List[File] = list()

        for manuscript in article.manuscript_files.all():
            files.append(manuscript)

        for data_file in article.data_figure_files.all():
            files.append(data_file)

        for source_file in article.source_files.all():
            files.append(source_file)

        for supplementary_file in article.supplementary_files.all():
            files.append(supplementary_file)

        return files

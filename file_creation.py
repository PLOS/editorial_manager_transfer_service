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

import logger_messages
from core.models import File
from journal.models import Journal
from plugins.editorial_manager_transfer_service.plugin_settings import EXPORT_FILE_PATH
from submission.models import Article
from utils import setting_handler
from utils.logger import get_logger

logger = get_logger(__name__)


def create_export_files(article_id: str, journal: Journal) -> List[str]:
    """
    Returns a list of file paths to the files to be exported.
    :param article_id: The id of the article.
    :param journal: The journal where the article is located.
    :return: A list of file paths to the paths to be exported.
    """
    file_creator: FileCreation = FileCreation(article_id, journal)

    return List([file_creator.get_zip_filepath(), file_creator.get_go_filepath()])


def get_article_export_folders() -> List[str]:
    """
    Gets the filepaths for the folders used for exporting articles.

    :return: A list of filepaths for the export folders.
    """
    if os.path.exists(EXPORT_FILE_PATH):
        return os.listdir(EXPORT_FILE_PATH)
    else:
        return []


class FileCreation:
    """
    A class for managing the export file creation process.
    """

    def __init__(self, article_id: str, journal: Journal):
        self.zip_filepath: str | None = None
        self.go_filepath: str | None = None
        self.license_code: str = setting_handler.get_setting(
            setting_group_name="plugin:editorial_manager_transfer_service", setting_name="license_code",
            journal=journal, ).processed_value
        self.journal_code: str = setting_handler.get_setting(
            setting_group_name="plugin:editorial_manager_transfer_service", setting_name="journal_code",
            journal=journal, ).processed_value
        self.submission_partner_code: str = setting_handler.get_setting(
            setting_group_name="plugin:editorial_manager_transfer_service", setting_name="submission_partner_code",
            journal=journal, ).processed_value

        export_folders: Sequence[str] = get_article_export_folders()
        self.export_folder: str | None = export_folders[0] if len(export_folders) > 0 else None

        self.__create_export_file(article_id)

    def get_zip_filepath(self) -> str | None:
        """
        Gets the zip file path for the exported files.
        :return: The zip file path.
        """
        if self.zip_filepath is None:
            return None
        else:
            return self.zip_filepath

    def get_go_filepath(self) -> str | None:
        """
        Gets the filepath for the go.xml file for exporting to Editorial Manager.
        :return: The filepath for the go.xml file or None, if the process failed.
        """
        if self.go_filepath is None:
            return None
        else:
            return self.go_filepath

    def __create_export_file(self, article_id: str):
        """
        Creates the export file for
        :param article_id: The ID of the article to create an export file for.
        :return: The filepath to the created export file.
        """

        # Get the article based upon the given article ID.
        logger.info(logger_messages.process_fetching_article(article_id))
        try:
            article: Article = self.__fetch_article(article_id)
        except Exception:
            logger.error(logger_messages.process_failed_fetching_article(article_id))
            return

        # Attempt to create the metadata file.
        metadata_file: File | None = self.__create_metadata_file(article)
        if metadata_file is None:
            logger.error(logger_messages.process_failed_fetching_metadata(article_id))
            return

        # Attempt to fetch the article files.
        article_files: Sequence[File] = self.fetch_article_files(article)
        if len(article_files) <= 0:
            logger.error(logger_messages.process_failed_fetching_article_files(article_id))
            return

        prefix: str = "{0}_{1}".format(self.submission_partner_code, uuid.uuid4())

        self.zip_filepath: str = os.path.join(self.export_folder, "{0}.zip".format(prefix))
        with zipfile.ZipFile(self.zip_filepath, "w") as zipf:
            zipf.write(metadata_file.get_file_path(article))
            for article_file in article_files:
                zipf.write(article_file.get_file_path(article))
            filenames: Sequence[str] = zipf.namelist()
            zipf.close()

        self.__create_go_xml_file(metadata_file.uuid_filename, filenames, prefix)

    def __create_go_xml_file(self, metadata_filename: str, article_filenames: Sequence[str], filename: str):
        """
        Creates the go xml file for the export process for Editorial Manager.
        :param metadata_filename: The name of the metadata file.
        :param article_filenames: The filenames of the article's associated files.
        :param filename: The name to use for the go.xml file (Must match the name of the zip file).
        """
        go: ETree.Element = ETree.Element("GO")
        go.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        go.set("xsi:noNamespaceSchemaLocation",
               "app://Aries.EditorialManager/Resources/XmlDefineTransformFiles/aries_import_go_file.xsd")

        # Format the header.
        header: ETree.Element = ETree.SubElement(go, "header")
        ETree.SubElement(header, "version", number="1.0")
        ETree.SubElement(header, "journal", code=self.journal_code)
        ETree.SubElement(header, "import-type", id="2")
        parameters: ETree.Element = ETree.SubElement(header, "parameters")
        ETree.SubElement(parameters, "parameter", name="license-code",
                         value="{0}_{1}".format(self.submission_partner_code, self.license_code))

        # Begin the filegroup.
        filegroup: ETree.Element = ETree.SubElement(go, "filegroup")

        # Create the archive and metadata files.
        ETree.SubElement(filegroup, "archive-file", name="{0}.zip".format(filename))
        ETree.SubElement(filegroup, "metadata-file", name=metadata_filename)

        for article_filename in article_filenames:
            ETree.SubElement(filegroup, "file", name=article_filename)

        tree = ETree.ElementTree(go)
        self.go_filepath = os.path.join(self.export_folder, "{0}.go.xml".format(filename))
        tree.write(self.go_filepath)

    @staticmethod
    def __fetch_article(article_id: str) -> Article:
        """
        Gets the article object for the given article ID.
        :param article_id: The ID of the article.
        :return: The article object with the given article ID.
        """
        return Article.get_article(article_id)

    def __create_metadata_file(self, article: Article) -> File | None:
        """
        Creates the metadata file based on the given article.
        :param article: The article to convert to JATS.
        :return:
        """
        pass

    @staticmethod
    def fetch_article_files(article: Article) -> List[File]:
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

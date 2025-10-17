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

import plugins.editorial_manager_transfer_service.consts as consts
import plugins.editorial_manager_transfer_service.logger_messages as logger_messages
from core.models import File
from journal.models import Journal
from plugins.editorial_manager_transfer_service.enums.report_state import ReportState
from plugins.editorial_manager_transfer_service.enums.transfer_log_message_type import TransferLogMessageType
from plugins.editorial_manager_transfer_service.models import TransferLogs
from plugins.editorial_manager_transfer_service.utils.jats import get_xml_license_code, generate_jats_metadata
from plugins.editorial_manager_transfer_service.utils.transfer_report import get_or_create_transfer_report, \
    resolve_transfer_report
from plugins.production_transporter.utilities import data_fetch
from plugins.editorial_manager_transfer_service.utils.settings import get_license_code, get_submission_partner_code, get_journal_code
from submission.models import Article
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

    def __init__(self, janeway_journal_code: str, article_id: int | None) -> None:
        self.zip_filepath: str | None = None
        self.go_filepath: str | None = None
        self.in_error_state: bool = False
        self.__license_code: str | None = None
        self.__journal_code: str | None = None
        self.__submission_partner_code: str | None = None
        self.article_id: int | None = article_id
        self.article: Article | None = None
        self.journal: Journal | None = None
        self.export_folder: str | None = None
        self.xml_filepath: str | None = None

        # Gets the journal
        self.journal: Journal | None = self.__fetch_journal(janeway_journal_code)
        if self.in_error_state:
            return

        # Get the article based upon the given article ID.
        self.article: Article | None = self.__fetch_article(self.journal, article_id)
        if self.in_error_state:
            return

        # Get the export folder.
        export_folders: str = get_article_export_folders()
        if len(export_folders) <= 0:
            self.log_error(logger_messages.export_process_failed_no_export_folder())
            self.in_error_state = True
            return
        self.export_folder = export_folders

        # Creates or fetches a report to track where this process is.
        self.transfer_report = get_or_create_transfer_report(self.journal, self.article)

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

        # Attempt to get the metadata file.
        if self.__get_xml_filepath() is None:
            logger.error(logger_messages.process_failed_fetching_metadata(self.article_id))
            self.in_error_state = True
            return

        # Attempt to fetch the article files.
        article_files: Sequence[File] = self.__fetch_article_files(self.article)
        if len(article_files) <= 0:
            self.log_error(logger_messages.process_failed_fetching_article_files(self.article_id))
            self.in_error_state = True
            return

        prefix: str = "{0}_{1}".format(self.get_submission_partner_code(), uuid.uuid4())

        self.zip_filepath: str = os.path.join(self.export_folder, "{0}.zip".format(prefix))
        with zipfile.ZipFile(self.zip_filepath, "w") as zipf:
            zipf.write(self.__get_xml_filepath())
            for article_file in article_files:
                zipf.write(article_file.get_file_path(self.article))
            filenames: Sequence[str] = zipf.namelist()
            zipf.close()

        # Remove the manuscript
        self.__create_go_xml_file(os.path.basename(self.__get_xml_filepath()), filenames, prefix)

    def get_license_code(self) -> str:
        """
        Gets the license code for exporting files.
        :return: The license code or None, if the process failed.
        """
        if not self.__license_code:
            self.__license_code: str = get_license_code(self.journal)
        return self.__license_code

    def get_journal_code(self) -> str:
        """
        Gets the journal code for exporting files.
        :return: The journal code or None, if the process failed.
        """
        if not self.__journal_code:
            self.__journal_code: str = get_journal_code(self.journal)
        return self.__journal_code

    def get_submission_partner_code(self) -> str:
        """
        Gets the submission partner code for exporting files.
        :return: The submission partner code or None, if the process failed.
        """
        if not self.__submission_partner_code:
            self.__submission_partner_code: str = get_submission_partner_code(self.journal)
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
        journal.set(consts.GO_FILE_JOURNAL_ELEMENT_ATTRIBUTE_CODE_KEY, self.get_journal_code())
        import_type: ETree.Element = ETree.SubElement(header, consts.GO_FILE_ELEMENT_TAG_IMPORT_TYPE)
        import_type.set(consts.GO_FILE_IMPORT_TYPE_ELEMENT_ATTRIBUTE_ID_KEY,
                        consts.GO_FILE_IMPORT_TYPE_ELEMENT_ATTRIBUTE_ID_VALUE)
        parameters: ETree.Element = ETree.SubElement(header, consts.GO_FILE_ELEMENT_TAG_PARAMETERS)
        parameter: ETree.Element = ETree.SubElement(parameters, consts.GO_FILE_ELEMENT_TAG_PARAMETER)
        parameter.set(consts.GO_FILE_ATTRIBUTE_ELEMENT_NAME_KEY, consts.GO_FILE_PARAMETER_ELEMENT_NAME_VALUE)
        parameter.set(consts.GO_FILE_PARAMETER_ELEMENT_VALUE_KEY, get_xml_license_code(self.journal))

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

    def __get_xml_filepath(self) -> str | None:
        """
        Creates the metadata file based on the given article.
        :return:The filepath to the JATS XML file.
        """
        if not self.xml_filepath:
            self.xml_filepath = generate_jats_metadata(self.journal, self.article, self.export_folder)
        return self.xml_filepath

    def __fetch_article(self, journal: Journal | None, article_id: int | None) -> Article | None:
        """
        Gets the article object for the given article ID.
        :param journal: The journal to fetch the article from.
        :param article_id: The ID of the article.
        :return: The article object with the given article ID.
        """
        logger.debug(logger_messages.process_fetching_article(article_id))

        article: Article | None = data_fetch.fetch_article(journal, article_id)
        if article is None:
            self.in_error_state = True
            return None

        logger.debug(logger_messages.process_finished_fetching_article(article_id))
        return article

    def __fetch_journal(self, janeway_journal_code: str | None) -> Journal | None:
        """
        Gets the journal from the database given the Janeway journal code.
        :param janeway_journal_code: The code of the Janeway journal to fetch.
        :return: The journal object with the given Janeway journal code, if there is one. None otherwise.
        """
        # Attempt to get the journal.
        logger.debug(logger_messages.process_fetching_journal(janeway_journal_code))

        journal: Journal | None = data_fetch.fetch_journal_data(janeway_journal_code)
        if journal is None:
            self.in_error_state = True
            return None

        logger.debug(logger_messages.process_finished_fetching_journal(janeway_journal_code))

        return journal

    def log_error(self, message: str, error: Exception = None,
                  stage: ReportState = ReportState.FAILED_BUNDLING) -> None:
        """
        Logs the given error message in both the database and plaintext logs.
        :param message: The message to log.
        :param error: The exception, if there is one.
        :param stage: Specify which stage this transfer is in.
        """
        logger.exception(error)
        logger.error(message)
        if self.transfer_report.report_state != stage:
            self.transfer_report.report_state = stage
            self.transfer_report.save()
        TransferLogs.objects.create(report=self.transfer_report, journal=self.journal, article=self.article,
                                    message=message,
                                    message_type=TransferLogMessageType.EXPORT, success=False)

    def log_success_go_file(self) -> None:
        """
        Logs a success message in both the database and plaintext logs.
        """
        TransferLogs.objects.create(report=self.transfer_report, journal=self.journal, article=self.article,
                                    message=logger_messages.export_go_file_process_succeeded(self.article_id),
                                    message_type=TransferLogMessageType.EXPORT, success=True)

    def log_success_zip_file(self) -> None:
        """
        Logs a success message in both the database and plaintext logs.
        """
        TransferLogs.objects.create(report=self.transfer_report, journal=self.journal, article=self.article,
                                    message=logger_messages.export_zip_file_process_succeeded(self.article_id),
                                    message_type=TransferLogMessageType.EXPORT, success=True)
        resolve_transfer_report(self.transfer_report)

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

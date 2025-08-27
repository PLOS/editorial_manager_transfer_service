"""
A list of functions handling file exports and imports.
"""
__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

import os
import uuid
import zipfile
import xml.etree.cElementTree as ET
from collections.abc import Sequence
from typing import List

from journal.models import Journal
from utils.logger import get_logger
from utils import setting_handler
import logger_messages

from submission.models import Article
from core.models import File

from plugins.editorial_manager_transfer_service.plugin_settings import EXPORT_FILE_PATH

logger = get_logger(__name__)


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
    def __init__(self, journal: Journal):
        self.zip_filepath = None
        self.go_filepath = None
        self.license_code: str = setting_handler.get_setting(
                setting_group_name="plugin:editorial_manager_transfer_service",
                setting_name="license_code",
                journal=journal,
            ).processed_value
        self.journal_code: str = setting_handler.get_setting(
            setting_group_name="plugin:editorial_manager_transfer_service",
            setting_name="journal_code",
            journal=journal,
        ).processed_value
        self.submission_partner_code: str = setting_handler.get_setting(
            setting_group_name="plugin:editorial_manager_transfer_service",
            setting_name="submission_partner_code",
            journal=journal,
        ).processed_value

        export_folders: Sequence[str] = get_article_export_folders()
        self.export_folder: str | None = export_folders[0] if len(export_folders) > 0 else None

    def create_export_file(self, article_id: str) -> str:
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
            return ""

        metadata_file: File = self.__create_metadata_file(article)
        article_files: List[File] = fetch_article_files(article)

        prefix: str = "{0}_{1}".format(self.submission_partner_code, uuid.uuid4())

        self.zip_filepath: str = os.path.join(self.export_folder, "{0}.zip".format(prefix))
        with zipfile.ZipFile(self.zip_filepath, "w") as zipf:
            zipf.write(metadata_file.get_file_path(article))
            for article_file in article_files:
                zipf.write(article_file.get_file_path(article))
            filenames: Sequence[str] = zipf.namelist()
            zipf.close()

        self.__create_go_xml_file(metadata_file.uuid_filename, filenames, prefix)

        return self.zip_filepath

    def __create_go_xml_file(self, metadata_filename: str, article_filenames: Sequence[str], filename: str) -> None:
        go: ET.Element = ET.Element("GO")
        go.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        go.set("xsi:noNamespaceSchemaLocation", "app://Aries.EditorialManager/Resources/XmlDefineTransformFiles/aries_import_go_file.xsd")

        # Format the header.
        header: ET.Element = ET.SubElement(go, "header")
        ET.SubElement(header, "version", number="1.0")
        ET.SubElement(header, "journal", code=self.journal_code)
        ET.SubElement(header, "import-type", id="2")
        parameters: ET.Element = ET.SubElement(header, "parameters")
        ET.SubElement(parameters, "parameter", name="license-code", value="{0}_{1}".format(self.submission_partner_code, self.license_code))

        # Begin the filegroup.
        filegroup: ET.Element = ET.SubElement(go, "filegroup")

        # Create the archive and metadata files.
        ET.SubElement(filegroup, "archive-file", name="{0}.zip".format(filename))
        ET.SubElement(filegroup, "metadata-file", name=metadata_filename)

        for article_filename in article_filenames:
            ET.SubElement(filegroup, "file", name=article_filename)

        tree = ET.ElementTree(go)
        self.go_filepath = os.path.join(self.export_folder, "{0}.go.xml".format(filename));
        tree.write(self.go_filepath)

    def __fetch_article(self, article_id: str) -> Article:
        # TODO: Finish method.
        pass

    def __create_metadata_file(self, article: Article) -> File:
        """
        Creates the metadata file based on the given article.
        :param article: The article to convert to JATS.
        :return:
        """
        pass


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







"""
This service is used to manage the transfers to and from Aries's Editorial Manager system.
"""
__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

import os
from typing import List

from plugins.editorial_manager_transfer_service.file_exporter import ExportFileCreation
from utils.logger import get_logger

logger = get_logger(__name__)


class FileTransferService:
    """
    Manages the transfers to and from Aries's Editorial Manager system.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Constructor.
        """
        if not hasattr(self, '_initialized'):  # Prevent re-initialization on subsequent calls
            self.exports: dict[str, ExportFileCreation] = dict()
            self.files_to_delete: List[str] = list()
            self._initialized = True

    def get_export_file_creator(self, journal_code: str, article_id: str) -> ExportFileCreation | None:
        """
        Gets the export file creator for the given article.
        :param journal_code: The journal code of the journal where the article lives.
        :param article_id: The article id.
        :return: The export file creator.
        """

        dictionary_identifier: str = self.__get_dictionary_identifier(journal_code, article_id)

        if dictionary_identifier not in self.exports:
            file_creator = ExportFileCreation(journal_code, article_id)
            if file_creator.in_error_state:
                return None
            self.exports[dictionary_identifier] = file_creator
        return self.exports[dictionary_identifier]

    @staticmethod
    def __get_dictionary_identifier(journal_code: str, article_id: str) -> str:
        return f"{journal_code}-{article_id}"

    def get_export_zip_filepath(self, journal_code: str, article_id: str) -> str | None:
        """
        Gets the export zip file path for the given article.
        :param journal_code: The journal code of the journal the article lives in.
        :param article_id: The article id.
        :return: The export zip file path.
        """
        file_export_creator = self.get_export_file_creator(journal_code, article_id)
        return file_export_creator.get_zip_filepath() if file_export_creator else None

    def get_export_go_filepath(self, journal_code: str, article_id: str) -> str | None:
        """
        Gets the export go file path for the given article.
        :param journal_code: The journal code of the journal the article lives in.
        :param article_id: The article id.
        :return: The export go file path.
        """
        file_export_creator = self.get_export_file_creator(journal_code, article_id)
        return file_export_creator.get_go_filepath() if file_export_creator else None

    def delete_export_files(self, journal_code: str, article_id: str) -> None:
        dictionary_identifier: str = self.__get_dictionary_identifier(journal_code, article_id)
        if dictionary_identifier not in self.exports:
            return
        file_exporter = self.exports.pop(dictionary_identifier)

        self.files_to_delete.append(file_exporter.get_zip_filepath())
        self.files_to_delete.append(file_exporter.get_go_filepath())

        del file_exporter

    def __delete_files(self) -> None:
        for file in self.files_to_delete:
            if self.__delete_file(file):
                self.files_to_delete.remove(file)

    @staticmethod
    def __delete_file(filepath: str) -> bool:
        if not os.path.exists(filepath):
            return True
        try:
            os.remove(filepath)
        except OSError:
            return False

        return True


def get_export_zip_filepath(journal_code: str, article_id: str) -> str | None:
    """
    Gets the zip file path for a given article.
    :param journal_code: The journal code of the journal the article lives in.
    :param article_id: The article id.
    :return: The zip file path.
    """
    return FileTransferService().get_export_zip_filepath(journal_code, article_id)


def get_export_go_filepath(journal_code: str, article_id: str) -> str | None:
    """
    Gets the export file path for a go file created for a given article.
    :param journal_code: The journal code of the journal the article lives in.
    :param article_id: The article id.
    :return: The export go file path.
    """
    return FileTransferService().get_export_go_filepath(journal_code, article_id)


def export_success_callback(journal_code: str, article_id: str) -> None:
    """
    The callback in case of a successful export.
    :param journal_code: The journal code of the journal the article lives in.
    :param article_id: The article id.
    """
    FileTransferService().delete_export_files(journal_code, article_id)


def export_failure_callback(journal_code: str, article_id: str) -> None:
    """
    The callback in case of a failed export.
    :param journal_code: The journal code of the journal the article lives in.
    :param article_id: The article id.
    """
    FileTransferService().delete_export_files(journal_code, article_id)

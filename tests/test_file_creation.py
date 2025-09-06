import os
import re
import shutil
import xml.etree.ElementTree as ElementTree
from typing import Sequence
from unittest.mock import patch

import hypothesis.strategies as hypothesis_strategies
from hypothesis import settings as hypothesis_settings, given
from hypothesis.extra.django import TestCase

import plugins.editorial_manager_transfer_service.consts as consts
import plugins.editorial_manager_transfer_service.file_exporter as file_exporter
import plugins.editorial_manager_transfer_service.tests.utils.article_creation_utils as article_utils
from journal.models import Journal
from plugins.editorial_manager_transfer_service.enums.transfer_log_message_type import TransferLogMessageType
from plugins.editorial_manager_transfer_service.models import TransferLogs

uuid4_regex = re.compile('^([a-z0-9]{8}(-[a-z0-9]{4}){3}-[a-z0-9]{12})$')
valid_filename_regex = re.compile("^[\w\-. ]+$")

valid_filenames: hypothesis_strategies.SearchStrategy[list[str]] = hypothesis_strategies.lists(
    hypothesis_strategies.from_regex(valid_filename_regex), unique=True, min_size=0,
    max_size=20)


def _get_setting(self, setting_name: str) -> str:
    match setting_name:
        case consts.PLUGIN_SETTINGS_LICENSE_CODE:
            return "LCODE"
        case consts.PLUGIN_SETTINGS_JOURNAL_CODE:
            return "JOURNAL"
        case consts.PLUGIN_SETTINGS_SUBMISSION_PARTNER_CODE:
            return "SUBMISSION_PARTNER"


class TestFileCreation(TestCase):
    def setUp(self):
        """
        Sets up the export folder structure.
        """
        if not os.path.exists(article_utils._get_article_export_folders()):
            try:
                os.makedirs(article_utils._get_article_export_folders())
            except FileExistsError:
                pass

    def tearDown(self):
        """
        Tears down after each test to ensure each test is unique.
        """
        shutil.rmtree(article_utils._get_article_export_folders())

    @given(article_id=hypothesis_strategies.from_regex(uuid4_regex),
           manuscript_filename=hypothesis_strategies.from_regex(valid_filename_regex),
           data_figure_filenames=valid_filenames)
    @patch.object(file_exporter.ExportFileCreation, 'get_setting', new=_get_setting)
    @patch('plugins.editorial_manager_transfer_service.file_exporter.get_article_export_folders',
           new=article_utils._get_article_export_folders)
    @patch.object(Journal.objects, "get", new=article_utils._get_journal)
    @patch('submission.models.Article.get_article')
    @hypothesis_settings(max_examples=5)
    def test_regular_article_creation_process(self, mock_get_article, article_id: str, manuscript_filename: str,
                                              data_figure_filenames: Sequence[str]):
        """
        Tests a basic end to end use case of exporting articles.
        :param mock_get_article: Mock the get_article method.
        :param article_id: The id of the article.
        """
        journal_code = "TEST"

        # Set the return
        mock_get_article.return_value = article_utils._create_article(Journal.objects.get(code=journal_code),
                                                                      article_id, manuscript_filename,
                                                                      data_figure_filenames)

        exporter = file_exporter.ExportFileCreation(journal_code, article_id)
        self.assertTrue(exporter.can_export())
        self.assertEqual(article_id.strip(), exporter.article_id)  # add assertion here

        self.__check_go_file(exporter.get_go_filepath(), len(data_figure_filenames) + 1)

    @given(message=hypothesis_strategies.text(),
           message_type=hypothesis_strategies.sampled_from(TransferLogMessageType.choices),
           success=hypothesis_strategies.booleans())
    def test_blank_transfer_logs(self, message: str, message_type: TransferLogMessageType, success: bool):
        """
        Tests creating an empty TransferLogs object.
        """
        TransferLogs.objects.create(
                journal=None,
                article=None,
                message=message,
                message_type=message_type,
                success=success
        )

    def __check_go_file(self, go_filepath: str, number_of_files: int) -> None:
        if not os.path.exists(go_filepath):
            self.fail("Go_filepath {} does not exist".format(go_filepath))

        # Get the XML file.
        try:
            tree = ElementTree.parse(go_filepath)
        except ElementTree.ParseError:
            self.fail("Go_filepath {} could not be parsed".format(go_filepath))

        root: ElementTree.Element = tree.getroot()
        self.assertIsNotNone(root)
        self.assertEqual(consts.GO_FILE_ELEMENT_TAG_GO, root.tag)

        filegroup: ElementTree.Element = root.find(consts.GO_FILE_ELEMENT_TAG_FILEGROUP)
        self.assertIsNotNone(filegroup)
        self.assertEqual(consts.GO_FILE_ELEMENT_TAG_FILEGROUP, filegroup.tag)

        files: list[ElementTree.Element] = filegroup.findall(consts.GO_FILE_ELEMENT_TAG_FILE)
        self.assertEqual(number_of_files, len(files))

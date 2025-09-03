import os
import re
import shutil
import unittest
import xml.etree.ElementTree as ElementTree
from typing import Sequence
from unittest.mock import patch

from hypothesis import given
from hypothesis import settings as hypothesis_settings
from hypothesis.strategies import from_regex, SearchStrategy, lists

import plugins.editorial_manager_transfer_service.consts as consts
import plugins.editorial_manager_transfer_service.file_exporter as file_creation
import plugins.editorial_manager_transfer_service.tests.utils.article_creation_utils as article_utils

uuid4_regex = re.compile('^([a-z0-9]{8}(-[a-z0-9]{4}){3}-[a-z0-9]{12})$')
valid_filename_regex = re.compile("^[\w\-. ]+$")

valid_filenames: SearchStrategy[list[str]] = lists(from_regex(valid_filename_regex), unique=True, min_size=0,
                                                   max_size=20)


def _get_setting(self, setting_name: str) -> str:
    match setting_name:
        case consts.PLUGIN_SETTINGS_LICENSE_CODE:
            return "LCODE"
        case consts.PLUGIN_SETTINGS_JOURNAL_CODE:
            return "JOURNAL"
        case consts.PLUGIN_SETTINGS_SUBMISSION_PARTNER_CODE:
            return "SUBMISSION_PARTNER"


class TestFileCreation(unittest.TestCase):
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

    @given(article_id=from_regex(uuid4_regex), manuscript_filename=from_regex(valid_filename_regex),
           data_figure_filenames=valid_filenames)
    @patch.object(file_creation.ExportFileCreation, 'get_setting', new=_get_setting)
    @patch('plugins.editorial_manager_transfer_service.file_creation.get_article_export_folders',
           new=article_utils._get_article_export_folders)
    @patch('submission.models.Article.get_article')
    @hypothesis_settings(max_examples=5)
    def test_regular_article_creation_process(self, mock_get_article, article_id: str, manuscript_filename: str,
                                              data_figure_filenames: Sequence[str]):
        """
        Tests a basic end to end use case of exporting articles.
        :param mock_get_article: Mock the get_article method.
        :param article_id: The id of the article.
        """
        # Set the return
        mock_get_article.return_value = article_utils._create_article(article_id, manuscript_filename,
                                                                      data_figure_filenames)

        exporter = file_creation.ExportFileCreation(article_id)
        self.assertTrue(exporter.can_export())
        self.assertEqual(article_id.strip(), exporter.article_id)  # add assertion here

        self.__check_go_file(exporter.get_go_filepath(), len(data_figure_filenames) + 1)

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


if __name__ == '__main__':
    unittest.main()

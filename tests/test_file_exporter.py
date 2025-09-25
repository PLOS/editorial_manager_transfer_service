__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

import os
import shutil
import xml.etree.ElementTree as ElementTree
from unittest.mock import patch

from hypothesis import settings as hypothesis_settings, given
from hypothesis.extra.django import TestCase

import plugins.editorial_manager_transfer_service.consts as consts
import plugins.editorial_manager_transfer_service.file_exporter as file_exporter
import plugins.editorial_manager_transfer_service.tests.utils.article_creation_utils as article_utils
from submission.models import Article


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
        article_utils.database_crafter_do_preqs()
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

    @given(article=article_utils.create_article())
    @patch.object(file_exporter.ExportFileCreation, 'get_setting', new=_get_setting)
    @patch('plugins.editorial_manager_transfer_service.file_exporter.get_article_export_folders',
           new=article_utils._get_article_export_folders)
    @hypothesis_settings(max_examples=5)
    def test_regular_article_creation_process(self, article: Article) -> None:
        """
        Tests a basic end to end use case of exporting articles.
        """
        journal = article.journal
        article_id: int = article.pk

        exporter = file_exporter.ExportFileCreation(journal.code, article_id)
        self.assertTrue(exporter.can_export())
        self.assertEqual(article_id, exporter.article_id)  # add assertion here

        self.__check_go_file(exporter.get_go_filepath(), len(article.data_figure_files.all()) + 1)

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

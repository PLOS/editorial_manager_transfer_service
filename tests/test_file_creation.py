import os
import re
import shutil
import unittest
import xml.etree.ElementTree as ElementTree
from unittest.mock import patch, MagicMock

from django.conf import settings
from hypothesis import given
from hypothesis import settings as hypothesis_settings
from hypothesis.strategies import from_regex

import plugins.editorial_manager_transfer_service.consts as consts
import plugins.editorial_manager_transfer_service.file_creation as file_creation
from core.models import File
from journal.models import Journal
from submission.models import Article

uuid4_regex = re.compile('^([a-z0-9]{8}(-[a-z0-9]{4}){3}-[a-z0-9]{12})$')

EXPORT_FOLDER = os.path.join(settings.BASE_DIR, "collected-static", consts.SHORT_NAME, "export")


def _get_setting(self, setting_name: str) -> str:
    match setting_name:
        case consts.PLUGIN_SETTINGS_LICENSE_CODE:
            return "LCODE"
        case consts.PLUGIN_SETTINGS_JOURNAL_CODE:
            return "JOURNAL"
        case consts.PLUGIN_SETTINGS_SUBMISSION_PARTNER_CODE:
            return "SUBMISSION_PARTNER"


def _get_article_export_folders() -> str:
    """
    Gets the filepaths for the folders used for exporting articles.

    :return: A list of filepaths for the export folders.
    """
    return EXPORT_FOLDER


def _get_journal() -> Journal:
    return MagicMock(Journal)


def _create_manuscript_file(filename: str) -> File:
    manuscript_filepath = os.path.join(_get_article_export_folders(), "{0}.txt".format(filename))
    content = "This is the first line.\nThis is the second line."
    with open(manuscript_filepath, 'w') as file:
        try:
            file.write(content)
            file.close()
        except FileExistsError:
            pass

        manuscript: File = MagicMock(File)
        manuscript.get_file_path.return_value = manuscript_filepath

        return manuscript


def _create_article(article_id: str, manuscript_filename: str) -> Article:
    manuscript: File = _create_manuscript_file(manuscript_filename)

    article: Article = MagicMock(Article)
    article.article_id = article_id
    article.journal = _get_journal()

    # Handle the manuscript files.
    article.manuscript_files = MagicMock(File.objects)
    manuscript_files: list[File] = list()
    manuscript_files.append(manuscript)
    article.manuscript_files.all.return_value = manuscript_files
    return article


class TestFileCreation(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(EXPORT_FOLDER):
            try:
                os.makedirs(EXPORT_FOLDER)
            except FileExistsError:
                pass

    def tearDown(self):
        """
        Tears down after each test to ensure each test is unique.
        """
        shutil.rmtree(EXPORT_FOLDER)

    @given(article_id=from_regex(uuid4_regex), manuscript_filename=from_regex(uuid4_regex))
    @patch.object(file_creation.ExportFileCreation, 'get_setting', new=_get_setting)
    @patch('plugins.editorial_manager_transfer_service.file_creation.get_article_export_folders',
           new=_get_article_export_folders)
    @patch('submission.models.Article.get_article')
    @hypothesis_settings(max_examples=5)
    def test_regular_article_creation_process(self, mock_get_article, article_id: str, manuscript_filename: str):
        """
        Tests a basic end to end use case of exporting articles.
        :param mock_get_article: Mock the get_article method.
        :param article_id: The id of the article.
        """
        # Set the return
        mock_get_article.return_value = _create_article(article_id, manuscript_filename)

        exporter = file_creation.ExportFileCreation(article_id)
        self.assertTrue(exporter.can_export())
        self.assertEqual(article_id.strip(), exporter.article_id)  # add assertion here

        self.__check_go_file(exporter.get_go_filepath(), 1)

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

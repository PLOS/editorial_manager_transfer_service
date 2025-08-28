import os
import re
import unittest
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

    if not os.path.exists(EXPORT_FOLDER):
        try:
            os.makedirs(EXPORT_FOLDER)
            print("Created folder {}".format(EXPORT_FOLDER))
        except FileExistsError:
            pass
    return EXPORT_FOLDER


def get_journal() -> Journal:
    return MagicMock(Journal)


def create_manuscript_file(filename: str) -> File:
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


class TestFileCreation(unittest.TestCase):
    @given(article_id=from_regex(uuid4_regex), manuscript_filename=from_regex(uuid4_regex))
    @patch.object(file_creation.ExportFileCreation, 'get_setting', new=_get_setting)
    @patch('submission.models.Article.get_article')
    @hypothesis_settings(max_examples=5)
    def test_something(self, mock_get_article, article_id: str, manuscript_filename: str):
        """
        Tests a basic end to end use case of exporting articles.
        :param mock_get_article: Mock the get_article method.
        :param article_id: The id of the article.
        """
        with patch(
                'plugins.editorial_manager_transfer_service.file_creation.get_article_export_folders') as mock_get_folders:
            manuscript: File = create_manuscript_file(manuscript_filename)

            mock_get_folders.return_value = _get_article_export_folders()
            article: Article = MagicMock(Article)
            article.article_id = article_id
            article.journal = get_journal()

            # Handle the manuscript files.
            article.manuscript_files = MagicMock(File.objects)
            manuscript_files: list[File] = list()
            manuscript_files.append(manuscript)
            article.manuscript_files.all.return_value = manuscript_files

            # Set the return
            mock_get_article.return_value = article

            exporter = file_creation.ExportFileCreation(article_id)
            self.assertTrue(exporter.can_export())
            self.assertEqual(article_id.strip(), exporter.article_id)  # add assertion here

    def tearDown(self):
        pass
        # shutil.rmtree(EXPORT_FOLDER)


if __name__ == '__main__':
    unittest.main()

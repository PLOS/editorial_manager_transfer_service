import os
from typing import Sequence
from unittest.mock import MagicMock

from core import settings
from core.models import File
from journal.models import Journal
from plugins.editorial_manager_transfer_service import consts
from submission.models import Article

EXPORT_FOLDER = os.path.join(settings.BASE_DIR, "collected-static", consts.SHORT_NAME, "export")


def _get_article_export_folders() -> str:
    """
    Gets the filepaths for the folders used for exporting articles.

    :return: A list of filepaths for the export folders.
    """
    return EXPORT_FOLDER


def _get_journal() -> Journal:
    return MagicMock(Journal)


def _create_txt_file(filename: str) -> File:
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


def _create_article(article_id: str, manuscript_filename: str, data_figure_filenames: Sequence[str]) -> Article:
    manuscript: File = _create_txt_file(manuscript_filename)

    article: Article = MagicMock(Article)
    article.article_id = article_id
    article.journal = _get_journal()

    # Handle the manuscript files.
    article.manuscript_files = MagicMock(File.objects)
    manuscript_files: list[File] = list()
    manuscript_files.append(manuscript)
    article.manuscript_files.all.return_value = manuscript_files

    # Handle the
    article.data_figure_files = MagicMock(File.objects)
    data_figure_files: list[File] = list()
    for data_figure_filename in data_figure_filenames:
        data_figure: File = _create_txt_file(data_figure_filename)
        data_figure_files.append(data_figure)
    article.data_figure_files.all.return_value = data_figure_files
    return article

__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

import codecs
import json
import os
import re

from django.conf import settings as django_settings
from django.core.files import File as DjangoFile
from hypothesis import strategies as st
from hypothesis.extra.django import from_field

from core import (
    models as core_models,
    files as core_files,
)
from core import settings
from core.models import File, Account
from journal.models import Journal
from plugins.editorial_manager_transfer_service import consts
from submission.models import Article

uuid4_regex = re.compile('^([a-z0-9]{8}(-[a-z0-9]{4}){3}-[a-z0-9]{12})$')
valid_filename_regex = re.compile("^[\w\-. ]+$")

EXPORT_FOLDER = os.path.join(settings.BASE_DIR, "collected-static", consts.SHORT_NAME, "export")


def _get_article_export_folders() -> str:
    """
    Gets the filepaths for the folders used for exporting articles.

    :return: A list of filepaths for the export folders.
    """
    return EXPORT_FOLDER


def database_crafter_do_preqs() -> None:
    """
    A number of items are required to be setup in advance within the database.
    """
    create_default_settings()
    database_crafter_create_default_xsl()


def create_default_settings() -> None:
    """
    Creates the default settings for to test this plugin.
    """
    with codecs.open(
            os.path.join(settings.BASE_DIR, "utils/install/submission_items.json")
    ) as json_data:
        submission_items = json.load(json_data)
        for i, setting in enumerate(submission_items):
            if not setting.get("group") == "special":
                setting_group_obj, c = core_models.SettingGroup.objects.get_or_create(
                        name=setting.get("group"),
                )
                core_models.Setting.objects.get_or_create(
                        group=setting_group_obj,
                        name=setting.get("name"),
                )


def database_crafter_create_default_xsl() -> None:
    """
    Creates the default XSL file if it doesn't exist.
    """
    try:
        core_models.XSLFile.objects.get(label=django_settings.DEFAULT_XSL_FILE_LABEL)
    except core_models.XSLFile.DoesNotExist:
        core_models.XSLFile.objects.create(label=django_settings.DEFAULT_XSL_FILE_LABEL)


@st.composite
def create_journal(draw) -> Journal:
    """
    Creates a journal object from the given settings.
    :param draw: The Hypothesis object provided by the hypothesis framework.
    :return: The newly created journal.
    """
    code = draw(st.text(min_size=1, max_size=40))
    journal: Journal = Journal.objects.create(code=code)
    return journal


@st.composite
def create_username(draw) -> str | None:
    """
    Creates a unique username or None, if the username created was not unique.
    :param draw: The Hypothesis object provided by the hypothesis framework.
    :return: A unique username or None, if the username created was not unique.
    """
    username = draw(from_field(Account._meta.get_field('username')))
    try:
        Account.objects.get(username=username)
        return None
    except Account.DoesNotExist:
        return username


@st.composite
def create_unique_email(draw) -> str | None:
    """
    Creates a unique email address or None, if the email address was not unique.
    :param draw: A Hypothesis object provided by the hypothesis framework.
    :return: A unique email address or None, if the email address was not unique.
    """
    email = draw(st.emails())
    try:
        Account.objects.get(email=email)
        return None
    except Account.DoesNotExist:
        return email


@st.composite
def create_account(draw) -> Account:
    """
    Creates a new account object from the given settings.
    :param draw: A Hypothesis object provided by the hypothesis framework.
    :return: A newly created account.
    """
    username = draw(create_username())
    while not username:
        username = draw(create_username())

    email = draw(create_unique_email())
    while not email:
        email = draw(create_unique_email())

    return Account.objects.create(
            email=email,
            username=username,
    )


@st.composite
def create_txt_file(draw, article: Article) -> File:
    filename: str = draw(st.from_regex(valid_filename_regex))
    manuscript_filepath = os.path.join(_get_article_export_folders(),
                                       "{0}.txt".format(filename))
    content = "This is the first line.\nThis is the second line."
    with open(manuscript_filepath, 'w') as file:
        try:
            file.write(content)
            file.flush()
            file.close()
        except FileExistsError:
            pass
    with open(manuscript_filepath, 'rb+') as file:
        django_file = DjangoFile(file, name=filename)
        return core_files.save_file_to_article(file_to_handle=django_file, article=article,
                                               owner=draw(create_account()))


@st.composite
def create_article(draw) -> Article:
    journal: Journal = draw(create_journal())
    article: Article = Article.objects.create(
            journal=journal,
    )

    manuscript: File = draw(create_txt_file(article=article))
    article.manuscript_files.add(manuscript)

    # Handle the data figure files.
    number_of_files: int = draw(st.integers(min_value=0, max_value=20))
    for i in range(number_of_files):
        data_figure: File = draw(create_txt_file(article=article))
        article.data_figure_files.add(data_figure)

    article.save()

    return article

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
from hypothesis.strategies import characters

from core import (
    models as core_models,
    files as core_files,
)
from core import settings
from core.models import File, Account, Setting, SettingGroup, setting_types, SettingValue
from journal.models import Journal
from plugins.editorial_manager_transfer_service import consts
from submission.models import Article, Field, FieldAnswer

uuid4_regex = re.compile('^([a-z0-9]{8}(-[a-z0-9]{4}){3}-[a-z0-9]{12})$')
valid_filename_regex = re.compile("^[\w\-. ]+$")
journal_code_regex = re.compile('^([a-z0-9]{1,40})$')

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


def create_group_setting(group_name: str) -> SettingGroup:
    setting, created = SettingGroup.objects.get_or_create(name=group_name)
    return setting


@st.composite
def create_setting(draw, group_name: str, setting_name: str) -> Setting:
    setting_group: SettingGroup = create_group_setting(group_name=group_name)
    setting, created = Setting.objects.get_or_create(name=setting_name, group=setting_group)
    if created:
        pretty_name = draw(st.text(min_size=1))
        description = draw(st.text(min_size=1))
        is_translatable = draw(st.booleans())
        setting_type = draw(st.sampled_from(setting_types))
        setting.defaults = {
            "pretty_name": pretty_name,
            "description": description,
            "is_translatable": is_translatable,
            "type": setting_type,
        }
        setting.save()

    return setting


@st.composite
def create_setting_value(draw, journal: Journal, group_name: str, setting_name: str, setting_value) -> SettingValue:
    setting = draw(create_setting(group_name=group_name, setting_name=setting_name))
    value = SettingValue.objects.filter(setting=setting, journal=journal).first()
    if not value:
        SettingValue.objects.create(setting=setting, journal=journal, value=setting_value)

    return value


@st.composite
def create_journal(draw) -> Journal:
    """
    Creates a journal object from the given settings.
    :param draw: The Hypothesis object provided by the hypothesis framework.
    :return: The newly created journal.
    """
    code: str = draw(st.from_regex(journal_code_regex))
    code = code.strip()
    name = draw(st.text(min_size=1))
    journal: Journal = Journal.objects.create(code=code)

    draw(create_setting_value(journal=journal, group_name="general", setting_name="journal_name", setting_value=name))
    return journal


@st.composite
def create_field(draw, journal: Journal) -> Field:
    name = draw(st.text(alphabet=characters(codec='utf-8'), min_size=1, max_size=40))
    order = 0
    field: Field = Field.objects.create(name=name, journal=journal, order=order)
    return field


@st.composite
def create_answer_field(draw, article: Article) -> FieldAnswer:
    answer = draw(st.text(alphabet=characters(codec='utf-8'), min_size=1, max_size=40))
    field: FieldAnswer = FieldAnswer.objects.create(field=draw(create_field(article.journal)), answer=answer,
                                                    article=article)
    return field


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
        django_file = DjangoFile(file, name=f"{filename}.txt")
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

    number_of_answers: int = draw(st.integers(min_value=0, max_value=20))
    for i in range(number_of_answers):
        draw(create_answer_field(article=article))

    article.save()

    return article

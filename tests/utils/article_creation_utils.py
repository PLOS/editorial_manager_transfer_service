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

from core import (models as core_models, files as core_files, settings as core_settings)
from core.models import File, Account, Setting, SettingGroup, setting_types, SettingValue, ControlledAffiliation, \
    Organization, OrganizationName, Location, Country, Role
from journal.models import Journal
from plugins.editorial_manager_transfer_service import consts
from submission.models import Article, Field, FieldAnswer, FrozenAuthor, ArticleFunding

ACCEPTABLE_CHARACTER_CATEGORIES = st.characters(blacklist_categories=["C", "S"], blacklist_characters=['&'])
EXPORT_FOLDER = os.path.join(core_settings.BASE_DIR, "collected-static", consts.SHORT_NAME, "export")

uuid4_regex = re.compile('^([a-z0-9]{8}(-[a-z0-9]{4}){3}-[a-z0-9]{12})$')
valid_filename_regex = re.compile("^[\w\-. ]+$")


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
    create_default_roles()


def create_default_roles() -> None:
    """
    Makes sure there is a role for authors.
    """
    Role.objects.get_or_create(slug="author")


def create_default_settings() -> None:
    """
    Creates the default settings for to test this plugin.
    """
    with codecs.open(os.path.join(core_settings.BASE_DIR, "utils/install/submission_items.json")) as json_data:
        submission_items = json.load(json_data)
        for i, setting in enumerate(submission_items):
            if not setting.get("group") == "special":
                setting_group_obj, c = core_models.SettingGroup.objects.get_or_create(name=setting.get("group"), )
                core_models.Setting.objects.get_or_create(group=setting_group_obj, name=setting.get("name"), )


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
def get_random_index(draw, obj_count: int) -> int | None:
    """
    Generates a random index for the given model.
    :param draw: The search strategy for the composite.
    :param obj_count: The number of objects which exist for the model.
    :return: A random index or None, if a random index should not be used.
    """

    # Decide if we want to create a new object or not
    if obj_count > 0:
        rando = draw(st.integers(min_value=1, max_value=100))
        if rando <= 75:
            return draw(st.integers(min_value=0, max_value=obj_count - 1))

    return None


@st.composite
def create_setting(draw, group_name: str, setting_name: str) -> Setting:
    setting_group: SettingGroup = create_group_setting(group_name=group_name)
    setting, created = Setting.objects.get_or_create(name=setting_name, group=setting_group)
    if created:
        pretty_name = draw(st.text(alphabet=ACCEPTABLE_CHARACTER_CATEGORIES, min_size=1))
        description = draw(st.text(alphabet=ACCEPTABLE_CHARACTER_CATEGORIES, min_size=1))
        is_translatable = draw(st.booleans())
        setting_type = draw(st.sampled_from(setting_types))
        setting.defaults = {"pretty_name": pretty_name, "description": description, "is_translatable": is_translatable,
                            "type": setting_type, }
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
    rand_index = draw(get_random_index(Journal.objects.count()))
    if rand_index is not None:
        return Journal.objects.all().order_by("id")[rand_index]

    code: str = draw(st.text(alphabet=ACCEPTABLE_CHARACTER_CATEGORIES, min_size=1, max_size=40))
    code = code.strip()
    name = draw(st.text(alphabet=ACCEPTABLE_CHARACTER_CATEGORIES, min_size=1))
    journal: Journal = Journal.objects.create(code=code)

    draw(create_setting_value(journal=journal, group_name="general", setting_name="journal_name", setting_value=name))
    return journal


@st.composite
def create_field(draw, journal: Journal) -> Field:
    name = draw(st.text(alphabet=ACCEPTABLE_CHARACTER_CATEGORIES, min_size=1, max_size=40))
    order = 0
    slug = draw(st.from_regex(uuid4_regex)).strip()
    field: Field = Field.objects.create(name=name, slug=slug, journal=journal, order=order)
    return field


@st.composite
def create_answer_field(draw, article: Article) -> FieldAnswer:
    answer = draw(st.text(alphabet=ACCEPTABLE_CHARACTER_CATEGORIES, min_size=1, max_size=40))
    field: FieldAnswer = FieldAnswer.objects.create(field=draw(create_field(article.journal)), answer=answer,
                                                    article=article)
    return field


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
def create_country(draw) -> Country:
    # Decide if we want to create a new country or not.
    rand_index = draw(get_random_index(Country.objects.count()))
    if rand_index is not None:
        return Country.objects.all().order_by("id")[rand_index]

    code = draw(st.text(alphabet=ACCEPTABLE_CHARACTER_CATEGORIES, min_size=1, max_size=5))
    name = draw(st.text(alphabet=ACCEPTABLE_CHARACTER_CATEGORIES, min_size=1, max_size=255))
    return Country.objects.create(code=code, name=name)


@st.composite
def create_location(draw) -> Location:
    # Decide if we want to create a new location or not.
    rand_index = draw(get_random_index(Location.objects.count()))
    if rand_index is not None:
        return Location.objects.all().order_by("id")[rand_index]

    city_name = draw(st.text(alphabet=ACCEPTABLE_CHARACTER_CATEGORIES, min_size=1, max_size=200))
    country = draw(create_country())
    return Location.objects.create(name=city_name, country=country)


@st.composite
def create_organization_name(draw, organization: Organization) -> OrganizationName:
    value = draw(st.text(alphabet=ACCEPTABLE_CHARACTER_CATEGORIES, min_size=1, max_size=1000))

    return OrganizationName.objects.create(value=value, ror_display_for=organization, label_for=organization, )


@st.composite
def create_organization(draw) -> Organization:
    # Decide if we want to create a new organization or not.
    rand_index = draw(get_random_index(Organization.objects.count()))
    if rand_index is not None:
        return Organization.objects.all().order_by("id")[rand_index]

    organization = Organization.objects.create()
    draw(create_organization_name(organization))
    location = draw(create_location())
    organization.locations.add(location)
    organization.save()
    return organization


@st.composite
def create_controlled_affiliation(draw, account: Account, is_primary: bool = False) -> ControlledAffiliation:
    title = draw(st.text(alphabet=ACCEPTABLE_CHARACTER_CATEGORIES, min_size=0, max_size=300))
    department = draw(st.text(alphabet=ACCEPTABLE_CHARACTER_CATEGORIES, min_size=0, max_size=300))

    start = draw(st.datetimes(allow_imaginary=False))
    end = None
    if not is_primary:
        should_end = draw(st.booleans())
        if should_end:
            end = draw(st.datetimes(allow_imaginary=False, min_value=start))

    organization = draw(create_organization())

    return ControlledAffiliation.objects.create(account=account, organization=organization, is_primary=is_primary,
                                                start=start, end=end, title=title, department=department, )


@st.composite
def create_account(draw) -> Account:
    """
    Creates a new account object from the given settings.
    :param draw: A Hypothesis object provided by the hypothesis framework.
    :return: A newly created account.
    """

    email = draw(create_unique_email())
    while not email:
        email = draw(create_unique_email())

    first_name = draw(st.text(alphabet=ACCEPTABLE_CHARACTER_CATEGORIES, min_size=1, max_size=300))
    middle_name = draw(st.text(alphabet=ACCEPTABLE_CHARACTER_CATEGORIES, min_size=0, max_size=300))
    last_name = draw(st.text(alphabet=ACCEPTABLE_CHARACTER_CATEGORIES, min_size=1, max_size=300))

    account = Account.objects.create(email=email, username=email.lower(), first_name=first_name,
                                     middle_name=middle_name, last_name=last_name, )

    # Make some affiliations
    draw(create_controlled_affiliation(account, is_primary=True))
    other_affiliations: int = draw(st.integers(min_value=0, max_value=5))
    for other_affiliation in range(other_affiliations):
        draw(create_controlled_affiliation(account, is_primary=False))

    return account


@st.composite
def create_txt_file(draw, article: Article) -> File:
    filename: str = draw(st.from_regex(valid_filename_regex))
    manuscript_filepath = os.path.join(_get_article_export_folders(), "{0}.txt".format(filename))
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
def create_frozen_author(draw, article: Article) -> FrozenAuthor:
    author = draw(create_account())
    return author.snapshot_as_author(article)

@st.composite
def create_funder(draw, article: Article) -> None:
    name = draw(st.text(alphabet=ACCEPTABLE_CHARACTER_CATEGORIES, min_size=1, max_size=500))
    fundref_id = draw(st.text(alphabet=ACCEPTABLE_CHARACTER_CATEGORIES, min_size=1, max_size=500))
    funding_id = draw(st.text(alphabet=ACCEPTABLE_CHARACTER_CATEGORIES, min_size=1, max_size=500))

    ArticleFunding.objects.create(name=name, article=article, fundref_id=fundref_id, funding_id=funding_id)

@st.composite
def create_funders(draw, article: Article) -> None:
    funders: int = draw(st.integers(min_value=1, max_value=3))
    for funder in range(funders):
        draw(create_funder(article))


@st.composite
def create_article(draw) -> Article:
    """
    Creates a new article object from the given settings.
    :param draw: The Hypothesis object provided by the hypothesis framework.
    :return: A randomly generated article.
    """
    title = draw(st.text(alphabet=ACCEPTABLE_CHARACTER_CATEGORIES, min_size=1, max_size=999))
    subtitle = draw(st.text(alphabet=ACCEPTABLE_CHARACTER_CATEGORIES, min_size=1, max_size=999))
    abstract = draw(st.text(alphabet=ACCEPTABLE_CHARACTER_CATEGORIES, min_size=1))
    journal: Journal = draw(create_journal())
    article: Article = Article.objects.create(title=title, subtitle=subtitle, abstract=abstract, journal=journal, )

    manuscript: File = draw(create_txt_file(article=article))
    article.manuscript_files.add(manuscript)

    # Handle the data figure files.
    number_of_files: int = draw(st.integers(min_value=0, max_value=5))
    for i in range(number_of_files):
        data_figure: File = draw(create_txt_file(article=article))
        article.data_figure_files.add(data_figure)

    # Add correspondence author.
    frozen_correspondence_author: FrozenAuthor = draw(create_frozen_author(article=article))
    article.correspondence_author = frozen_correspondence_author.author

    article.save()

    number_of_answers: int = draw(st.integers(min_value=0, max_value=5))
    for i in range(number_of_answers):
        draw(create_answer_field(article=article))

    number_of_authors: int = draw(st.integers(min_value=0, max_value=5))
    for i in range(number_of_authors):
        frozen_correspondence_author: FrozenAuthor = draw(create_frozen_author(article=article))
        frozen_correspondence_author.associate_with_account()
        frozen_correspondence_author.save()

    draw(create_funders(article=article))

    return article

__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

import codecs
import os
import uuid
from enum import Enum
from typing import List, TypedDict

from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.template.loader import render_to_string
from django.utils.safestring import SafeString

from core.models import Organization, File
from journal.models import Journal
from plugins.editorial_manager_transfer_service import consts
from plugins.editorial_manager_transfer_service.models import EditorialManagerSection
from plugins.editorial_manager_transfer_service.utils import settings
from plugins.editorial_manager_transfer_service.utils.data_fetch import (
    fetch_answer_fields_for_jats,
)
from plugins.editorial_manager_transfer_service.utils.interfaces.FrozenAuthorForJats import (
    JATSFrozenAuthor,
    JATSFrozenAffiliation,
    FrozenAuthorForJats,
)
from submission.models import Article, FieldAnswer, FrozenAuthor
from utils.logger import get_logger

logger = get_logger(__name__)


class JATSArticleTypeForEM(Enum):
    MANUSCRIPT = "Manuscript"
    DATA_FILE = "data_file"
    SOURCE_FILE = "source_file"
    SUPPLEMENTARY_FILE = "supplementary_file"


class JATSArticleFile(TypedDict):
    full_filename: str
    filepath: str
    filename: str
    file_type: str
    article_type: JATSArticleTypeForEM


def get_jats_article_file(
    filepath: str, article_type: JATSArticleTypeForEM
) -> JATSArticleFile:
    filename: str = os.path.basename(filepath)
    split_filename: list[str] = filename.split(".", 2)
    return JATSArticleFile(
        filepath=filepath,
        full_filename=filename,
        filename=split_filename[0],
        file_type=split_filename[1],
        article_type=article_type,
    )


def convert_file_to_jats_dict(
    article: Article, file: File, article_type: JATSArticleTypeForEM
) -> JATSArticleFile:
    """
    Converts the article file to a JATs-friendly dictionary.
    :param article: The article we're fetching files from.
    :param file: The file we're fetching information about.
    :param article_type: The type of this article.
    :return: The JATS-friendly dictionary.
    """
    filepath: str = file.get_file_path(article)
    return get_jats_article_file(filepath, article_type)


def generate_jats_metadata(
    journal: Journal, article: Article, article_folder: str
) -> str | None:
    """
    Generates JATS metadata for an article.
    :param journal: The journal the article lives within.
    :param article: The article to generate metadata for.
    :param article_folder: The folder under which the article is stored.
    :return: Gets the filepath of the generated JATS file
    """
    logger.debug("Generating JATS file...")

    if not article:
        logger.error("No article given")
        return None

    if not journal:
        logger.error("No journal given")
        return None

    if not article_folder:
        logger.error("No article folder given")
        return None

    template = consts.JATS_XML_FILE

    answer_fields: List[FieldAnswer] | None = fetch_answer_fields_for_jats(article)
    if answer_fields is None:
        answer_fields = []

    frozen_authors = fetch_author_metadata(article)

    em_section = fetch_em_section(article)

    files: List[JATSArticleFile] = list()

    for manuscript in article.manuscript_files.all():
        files.append(
            convert_file_to_jats_dict(
                article, manuscript, JATSArticleTypeForEM.MANUSCRIPT
            )
        )

    context = {
        "journal": journal,
        "article": article,
        "include_declaration": True,
        "body": True,
        "answer_fields": answer_fields,
        "license": get_xml_license_code(journal),
        "frozen_authors": frozen_authors,
        "em_section": em_section,
        "manuscript_files": files,
    }

    try:
        rendered_jats: SafeString = render_to_string(template, context)
        logger.debug("Generated JATS file.")
    except TemplateDoesNotExist as e:
        logger.exception("JATS file not found.", e)
        return None
    except TemplateSyntaxError as e:
        logger.exception(
            f"JATS template syntax error for article (ID: {article.pk}).", e
        )
        return None

    file_name = f"{uuid.uuid4()}_{article.pk}.xml"
    full_path = os.path.join(article_folder, file_name)

    with codecs.open(full_path, "w", "utf-8") as file:
        file.write(rendered_jats)
        file.close()

    return full_path


def fetch_em_section(article: Article) -> EditorialManagerSection | None:
    """
    Fetches the EM Section ID for use.
    :return: The EM section ID, if one can be located.
    """
    if not article or not article.section:
        return None

    section = article.section

    em_section = EditorialManagerSection.objects.filter(section=section).first()
    if not em_section:
        logger.debug(f"EM section not found for article (ID: {article.pk}).")
        return None

    return em_section


def fetch_author_metadata(article: Article) -> List[FrozenAuthorForJats]:
    """
    Fetches the metadata for an author.
    :param article: The article to fetch the author metadata for.
    :return: A list of authors and their affiliations.
    """
    frozen_authors = article.frozen_authors_for_jats_contribs()

    frozen_auths = []

    for frozen_author in frozen_authors:
        frozen_auth: FrozenAuthorForJats = FrozenAuthorForJats()

        author = frozen_author["author"]
        affiliations = frozen_author["affiliations"]

        frozen_auth.author = add_people_id(author)
        for affiliation in affiliations:
            frozen_auth.affiliations.append(add_ringgold_id_to_affiliation(affiliation))

        frozen_auths.append(frozen_auth)

    return frozen_auths


def add_people_id(author: FrozenAuthor) -> JATSFrozenAuthor:
    """
    Adds the EM people ID to the author using the email of the author.
    :param author: The author to fetch and add the People ID to.
    """
    # TODO: Fetch People ID
    people_id = author.pk

    return JATSFrozenAuthor(author, people_id)


def add_ringgold_id_to_affiliation(affiliation: Organization) -> JATSFrozenAffiliation:
    """
    Adds the Ringgold ID to the affiliation.
    :param affiliation: The affiliation to add the Ringgold ID to.
    """
    # TODO: Fetch Ringgold.
    ringgold_id = "1812"

    return JATSFrozenAffiliation(affiliation, ringgold_id)


def get_xml_license_code(journal: Journal) -> str:
    """
    Gets the license code for the XML.
    :param journal: The journal where the setting lives.
    :return: The XML license code.
    """
    return "{0}_{1}".format(
        settings.get_submission_partner_code(journal),
        settings.get_license_code(journal),
    )

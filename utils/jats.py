__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

import codecs
import os
import uuid
from typing import List

from core.models import Organization
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.template.loader import render_to_string
from django.utils.safestring import SafeString

from journal.models import Journal
from plugins.editorial_manager_transfer_service import consts
from plugins.editorial_manager_transfer_service.utils import settings
from plugins.editorial_manager_transfer_service.utils.data_fetch import fetch_answer_fields_for_jats
from submission.models import Article, FieldAnswer, FrozenAuthor
from utils.logger import get_logger

logger = get_logger(__name__)


def generate_jats_metadata(journal: Journal, article: Article, article_folder: str) -> str | None:
    """
    Generates JATS metadata for an article.
    :param journal: The journal the article lives within.
    :param article: The article to generate metadata for.
    :param article_folder: The folder under which the article is stored.
    :return: Gets the filepath of the generated JATS file
    """
    logger.debug('Generating JATS file...')

    if not article:
        logger.error('No article given')
        return None

    if not journal:
        logger.error('No journal given')
        return None

    if not article_folder:
        logger.error('No article folder given')
        return None

    template = consts.JATS_XML_FILE

    answer_fields: List[FieldAnswer] | None = fetch_answer_fields_for_jats(article)
    if answer_fields is None:
        answer_fields = []

    frozen_authors = fetch_author_metadata(article)

    context = {'journal': journal, 'article': article, 'include_declaration': True, 'body': True,
               'answer_fields': answer_fields, 'license': get_xml_license_code(journal), 'frozen_authors': frozen_authors,}

    try:
        rendered_jats: SafeString = render_to_string(template, context)
        logger.debug('Generated JATS file.')
    except TemplateDoesNotExist as e:
        logger.exception('JATS file not found.', e)
        return None
    except TemplateSyntaxError as e:
        logger.exception(f'JATS template syntax error for article (ID: {article.pk}).', e)
        return None

    file_name = f'{uuid.uuid4()}_{article.pk}.xml'
    full_path = os.path.join(article_folder, file_name)

    with codecs.open(full_path, 'w', "utf-8") as file:
        file.write(rendered_jats)
        file.close()

    return full_path

def fetch_author_metadata(article: Article) -> List[{author: FrozenAuthor, affiliations: List[Organization]}]:
    frozen_authors = article.frozen_authors_for_jats_contribs()

    for frozen_author in frozen_authors:
        author = frozen_author.author
        affiliations = author.affiliations

        add_people_id(author)
        for affiliation in affiliations:
            add_ringgold_id_to_affiliation(affiliation)


    return frozen_authors

def add_people_id(author: FrozenAuthor) -> None:
    """
    Adds the EM people ID to the author using the email of the author.
    :param author: The author to fetch and add the People ID to.
    """
    # TODO: Fetch People ID
    people_id = author.pk

    author['people_id'] = people_id

def add_ringgold_id_to_affiliation(affiliation) -> None:
    """
    Adds the Ringgold ID to the affiliation.
    :param affiliation: The affiliation to add the Ringgold ID to.
    """
    # TODO: Fetch Ringgold.
    affiliation.ringgold_id = "1812"

def get_xml_license_code(journal: Journal) -> str:
    """
    Gets the license code for the XML.
    :param journal: The journal where the setting lives.
    :return: The XML license code.
    """
    return "{0}_{1}".format(settings.get_submission_partner_code(journal), settings.get_license_code(journal))

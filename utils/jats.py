__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

import os
import uuid
import codecs

from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.template.loader import render_to_string
from django.utils.safestring import SafeString

from journal.models import Journal
from plugins.editorial_manager_transfer_service import consts
from plugins.editorial_manager_transfer_service.utils import settings
from plugins.editorial_manager_transfer_service.utils.data_fetch import fetch_answer_fields_for_jats
from submission.models import Article
from utils.logger import get_logger

logger = get_logger(__name__)

def generate_jats_metadata(journal: Journal, article: Article, article_folder: str) -> str | None:
    """

    :param journal:
    :param article:
    :param article_folder:
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

    answer_fields = fetch_answer_fields_for_jats(article)
    if not answer_fields:
        answer_fields = []

    context = {
        'article': article,
        'include_declaration': True,
        'body': True,
        'answer_fields': answer_fields,
        'license': get_xml_license_code(journal),
        'affiliations': []
    }

    try:
        rendered_jats: SafeString = render_to_string(template, context)
        logger.debug('Generated JATS file.')
    except TemplateDoesNotExist as e:
        logger.exception('JATS file not found.', e)
        return None
    except TemplateSyntaxError as e:
        logger.exception('JATS template syntax error for article {ID: {article_id}).'.format(article_id=article.pk), e)
        print('JATS template syntax error for article {ID: {article_id}).'.format(article_id=article.pk))
        print(e)
        return None

    file_name = '{uuid}_{id}.xml'.format(uuid=uuid.uuid4(), id=article.pk)
    full_path = os.path.join(article_folder, file_name)

    with codecs.open(full_path, 'w', "utf-8") as file:
        file.write(rendered_jats)
        file.close()

    return full_path

def get_xml_license_code(journal: Journal) -> str:
    """
    Gets the license code for the XML.
    :param journal: The journal where the setting lives.
    :return: The XML license code.
    """
    return "{0}_{1}".format(settings.get_submission_partner_code(journal), settings.get_license_code(journal))
__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

from typing import List

from django.core.cache import cache

from plugins.editorial_manager_transfer_service.utils.encoding import (
    encode_answer_field,
    JATSFieldAnswer,
)
from plugins.production_transporter.utilities.data_fetch import CACHE_TIMEOUT
from submission.models import FieldAnswer, Article
from utils.logger import get_logger

logger = get_logger(__name__)


def fetch_answer_fields_for_jats(
    article: Article, fetch_fresh: bool = False
) -> List[JATSFieldAnswer] | None:
    """
    Fetches the answer fields to use for jats generation.
    :param article: The article to fetch the fields for.
    :param fetch_fresh: True if we should ignore the cache and fetch new.
    :return: A list of the fields to use.
    """
    if not article:
        logger.error("No article provided.")
        return None

    if fetch_fresh:
        answer_fields: List[JATSFieldAnswer] | None = None
    else:
        answer_fields: List[JATSFieldAnswer] | None = cache.get(
            f"answer_fields_jats_{article.pk}", None
        )

    if not answer_fields:
        answer_fields_set = FieldAnswer.objects.filter(
            article=article
        ).prefetch_related("field")
        if answer_fields_set is None:
            logger.error(
                f"Couldn't fetch answer fields for article (ID: {article.pk})."
            )
            return None

        encoded_answer_field_set: List[JATSFieldAnswer] = []
        for answer_field in answer_fields_set:
            encoded_answer_field_set.append(encode_answer_field(answer_field))

        answer_fields = encoded_answer_field_set
        cache.set(
            f"answer_fields_jats_{article.pk}", encoded_answer_field_set, CACHE_TIMEOUT
        )

    return answer_fields

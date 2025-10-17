__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

from typing import List

from django.core.cache import cache

from plugins.production_transporter.utilities.data_fetch import CACHE_TIMEOUT
from submission.models import FieldAnswer, Article
from utils.logger import get_logger

logger = get_logger(__name__)

def fetch_answer_fields_for_jats(article: Article, fetch_fresh: bool = False) -> List[FieldAnswer] | None:
    if not article:
        logger.error("No article provided.")
        return None

    if fetch_fresh:
        answer_fields = None
    else:
        answer_fields = cache.get(f"answer_fields_jats_{article.pk}", None)

    if not answer_fields:
        answer_fields = Article.objects.filter(article=article).prefetch_related('field').values('field', 'answer').distinct()
        if not answer_fields:
            logger.error("Couldn't fetch answer fields.")
            return None
        cache.set(f"answer_fields_jats_{article.pk}", answer_fields, CACHE_TIMEOUT)

    return answer_fields
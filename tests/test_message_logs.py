__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

import os
import shutil

import hypothesis.strategies as hypothesis_strategies
from hypothesis import given
from hypothesis.extra.django import TestCase

import plugins.editorial_manager_transfer_service.tests.utils.article_creation_utils as article_utils
from plugins.editorial_manager_transfer_service.enums.transfer_log_message_type import TransferLogMessageType
from plugins.editorial_manager_transfer_service.models import TransferLogs
from submission.models import Article


class TestMessageLogs(TestCase):
    def setUp(self):
        """
        Sets up the export folder structure.
        """
        article_utils.database_crafter_do_preqs()
        if not os.path.exists(article_utils._get_article_export_folders()):
            try:
                os.makedirs(article_utils._get_article_export_folders())
            except FileExistsError:
                pass

    def tearDown(self):
        """
        Tears down after each test to ensure each test is unique.
        """
        shutil.rmtree(article_utils._get_article_export_folders())

    @given(message=hypothesis_strategies.text(),
           message_type=hypothesis_strategies.sampled_from(TransferLogMessageType.choices),
           success=hypothesis_strategies.booleans())
    def test_blank_transfer_logs(self, message: str, message_type: TransferLogMessageType, success: bool):
        """
        Tests creating an empty TransferLogs object.
        """
        TransferLogs.objects.create(
                journal=None,
                article=None,
                message=message,
                message_type=message_type,
                success=success
        )

    @given(article=article_utils.create_article(),
           message=hypothesis_strategies.text(),
           message_type=hypothesis_strategies.sampled_from(TransferLogMessageType.choices),
           success=hypothesis_strategies.booleans())
    def test_normal_transfer_logs(self, article: Article, message: str, message_type: TransferLogMessageType,
                                  success: bool):
        """
        Tests creating an empty TransferLogs object.
        """
        TransferLogs.objects.create(
                journal=article.journal,
                article=article,
                message=message,
                message_type=message_type,
                success=success
        )

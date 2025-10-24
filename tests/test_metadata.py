__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

import os
from unittest.mock import patch

from hypothesis import given, settings, HealthCheck
from hypothesis.extra.django import TestCase
from lxml import etree
from lxml.etree import ElementTree

import plugins.editorial_manager_transfer_service.tests.utils.article_creation_utils as article_utils
from plugins.editorial_manager_transfer_service.tests.utils.validate_jats import validate_xml
from plugins.editorial_manager_transfer_service.utils.jats import generate_jats_metadata
from submission.models import Article


def _get_submission_partner_code(self):
    return "SUBMISSION_PARTNER"


def _get_license_code(self):
    return "LCODE"


def _get_journal_code(self):
    return "JOURNAL_CODE"


settings.register_profile("single_run", max_examples=1)
settings.load_profile("single_run")


class TestMetadataCreation(TestCase):
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
        # shutil.rmtree(article_utils._get_article_export_folders())
        pass

    @settings(max_examples=1, derandomize=False, deadline=None,
              suppress_health_check=[HealthCheck.large_base_example, HealthCheck.too_slow])
    @given(article=article_utils.create_article())
    @patch("plugins.editorial_manager_transfer_service.utils.settings.get_submission_partner_code",
           new=_get_submission_partner_code)
    @patch('plugins.editorial_manager_transfer_service.utils.settings.get_license_code', new=_get_license_code)
    @patch('plugins.editorial_manager_transfer_service.utils.settings.get_journal_code', new=_get_journal_code)
    def test_regular_metadata(self, article: Article) -> None:
        """
        Tests a basic end to end use case of exporting articles.
        """
        journal = article.journal

        jats_filepath = generate_jats_metadata(journal, article, article_utils._get_article_export_folders())
        if (jats_filepath is None) or not os.path.exists(jats_filepath):
            self.fail(f"Metadata \"{jats_filepath}\" does not exist")

        # Get the XML file.
        parser = etree.XMLParser(remove_blank_text=True)
        try:
            tree: ElementTree = etree.parse(jats_filepath, parser=parser)
        except etree.ParseError:
            self.fail(f"Metadata {jats_filepath} could not be parsed")

        root = tree.getroot()
        self.assertIsNotNone(root)
        validate_xml(self, root, article)

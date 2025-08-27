"""
Commands for exporting and importing files to/form Aries's Editorial Manager.
"""

__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

from typing import Sequence

from django.core.management.base import BaseCommand, CommandError

import plugins.editorial_manager_transfer_service.file_creation as file_creation


class Command(BaseCommand):
    """Creates an export ZIP from an article."""

    help = "Creates an export ZIP from an article."

    def add_arguments(self, parser):
        parser.add_argument('article_id', help="The ID of the article to create a zip file for.")

    def handle(self, *args, **options):
        article_id: str = open(options["article_id"], "r", encoding="utf-8-sig").read().strip()

        print("Beginning bundling process for article...")
        export_files: Sequence[str] = file_creation.create_export_files(article_id)
        if not export_files:
            raise CommandError("Error while creating export ZIP.")

        print("Export files created.")

        # TODO: Initiate HTTP request to FTP server.

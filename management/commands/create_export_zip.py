"""
Commands for exporting and importing files to/form Aries's Editorial Manager.
"""

__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

from django.core.management.base import BaseCommand, CommandError

import plugins.editorial_manager_transfer_service.file_transfer_service as file_transfer_service


class Command(BaseCommand):
    """Creates an export ZIP from an article."""

    help = "Creates an export ZIP from an article."

    def add_arguments(self, parser):
        parser.add_argument('article_id', help="The ID of the article to create a zip file for.")
        parser.add_argument('journal_code', help="The code of the journal where the article to export lives.")

    def handle(self, *args, **options):
        article_id: str = open(options["article_id"], "r", encoding="utf-8-sig").read().strip()
        journal_code: str = open(options["journal_code"], "r", encoding="utf-8-sig").read().strip()

        print("Beginning bundling process for article...")
        export_zip_file: str = file_transfer_service.get_export_zip_filepath(journal_code, article_id)
        if not export_zip_file:
            raise CommandError("Error while creating export ZIP.")

        export_go_file: str = file_transfer_service.get_export_go_filepath(journal_code, article_id)
        if not export_go_file:
            raise CommandError("Error while creating export GO file.")

        print("Export files created.")

        # TODO: Initiate HTTP request to FTP server.

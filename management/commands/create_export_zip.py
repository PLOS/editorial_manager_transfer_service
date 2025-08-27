from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """Creates an export ZIP from an article."""

    help = "Creates an export ZIP from an article."

    def add_arguments(self, parser):
        parser.add_argument('article_id', help="The ID of the article to create a zip file for.")

    def handle(self, *args, **options):
        with open(options["article_id"], "r", encoding="utf-8-sig") as article_id:
            print("Beginning bundling process for article...")
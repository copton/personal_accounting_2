from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Populate the database with initial data"

    def handle(self, *args, **options):
        # Load initial data from the fixture file
        call_command("loaddata", "initial_data.json")

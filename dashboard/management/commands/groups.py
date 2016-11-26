from django.core.management.base import BaseCommand

from circles.models import Group

from reach.settings import GROUPS


class Command(BaseCommand):
    help = 'Create groups'

    def handle(self, *args, **options):
        for group in GROUPS:
            Group.objects.create(name=group)

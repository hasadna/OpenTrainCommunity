from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import data.utils

class Command(BaseCommand):
    args = ''
    help = 'fix trips start time'

    def handle(self, *args, **options):
        data.utils.fix_x_time()





from django.core.management import BaseCommand
import data.cache_utils

class Command(BaseCommand):
    args = ''
    help = 'Invalidates the Redis cache'

    def handle(self, *args, **kwargs):
        data.cache_utils.invalidate_cache()

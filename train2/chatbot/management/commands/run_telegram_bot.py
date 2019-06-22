import logging
from django.core.management import BaseCommand
from chatbot.tg_utils import setup_telegram_bot

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        updater = setup_telegram_bot()
        logger.info("Start polling")
        updater.start_polling()


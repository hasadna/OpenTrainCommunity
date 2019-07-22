import logging
from django.conf import settings
import telegram
from django.template.loader import render_to_string

from . import models


logger = logging.getLogger(__name__)


def get_broadcast_message(report: models.ChatReport):
    return render_to_string('chatbot/channel_message.html', context={
        'report': report,
    })


def broadcast_to_telegram_channel(report: models.ChatReport):
    try:
        bot = telegram.Bot(settings.TELEGRAM_TOKEN)
        message = get_broadcast_message(report)
        bot.send_message(settings.TELEGRAM_CHANNEL, message, parse_mode='html')
    except Exception:
        logger.exception('Failed to broadcast to channel')



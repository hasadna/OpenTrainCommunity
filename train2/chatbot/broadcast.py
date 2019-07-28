import logging
from django.conf import settings
import telegram
from django.template.loader import render_to_string

from . import models


logger = logging.getLogger(__name__)


def broadcast_new_report_to_telegram_channel(report: models.ChatReport):
    message = render_to_string('chatbot/new_report_message.html', context={
        'report': report,
    })
    _broadcast(message)


def broadcast_wrong_report_to_telegram_channel(report: models.ChatReport):
    message = render_to_string('chatbot/wrong_report_message.html', context={
        'report': report,
    })
    _broadcast(message)


def _broadcast(message: str):
    channel = '@' + settings.TELEGRAM_CHANNEL
    try:
        bot = telegram.Bot(settings.TELEGRAM_TOKEN)
        bot.send_message(channel, message, parse_mode='html')
    except Exception:
        logger.exception('Failed to broadcast to channel')





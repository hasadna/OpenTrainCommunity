import functools
import logging

import telegram
from django.conf import settings
from telegram.ext import Updater, Dispatcher, CommandHandler, MessageHandler, \
    Filters, CallbackQueryHandler

from chatbot.chat_utils import ChatUtils
from chatbot.consts import ChatPlatform
from common import slack_utils

logger = logging.getLogger(__name__)


def handle_error(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as ex:
            slack_utils.send_error(f'Failed in telegram: {ex}')
            logger.exception("Error in telegram: %s", ex)
    return wrapper


@handle_error
def cmd_start(bot, update):
    from . import views
    chat_id = update.message.chat_id
    logger.info("In start chat_id = %s", chat_id)
    views.handle_chat(ChatPlatform.TELEGRAM, update, bot=bot)


@handle_error
def cmd_catch_all(bot, update):
    chat_id = update.message.chat_id
    logger.info("In cmd_catch_all chat_id = %s", chat_id)
    cmd = update.message.text
    bot.send_message(
        chat_id=update.message.chat_id,
        text="מצטער, אני לא מכיר את הפקודה " + cmd
    )


@handle_error
def handle_reply(bot, update):
    from . import views
    logger.info("In handle_reply update = %s", ChatUtils.anonymize(update.to_json()))
    # note, we send here the full update object, not only the message
    # since for callback we need other members
    views.handle_chat(ChatPlatform.TELEGRAM, update, bot=bot)


def setup_telegram_bot():
    bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
    updater: Updater = Updater(bot=bot)
    dispatcher: Dispatcher = updater.dispatcher
    # handle the /start command
    dispatcher.add_handler(CommandHandler('start', cmd_start))
    # handle any other command
    dispatcher.add_handler(MessageHandler(Filters.command, cmd_catch_all))
    # handle text
    dispatcher.add_handler(MessageHandler(Filters.text, handle_reply))
    # handle video
    dispatcher.add_handler(MessageHandler(Filters.photo, handle_reply))
    # handle photo
    dispatcher.add_handler(MessageHandler(Filters.video, handle_reply))
    # handle buttons replies
    dispatcher.add_handler(CallbackQueryHandler(handle_reply))
    return updater
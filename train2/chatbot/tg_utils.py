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
def cmd_admin(bot, update):
    from . import managers
    managers.handle_cmd(bot, update)


@handle_error
def handle_admin_callback(bot, update):
    from . import managers
    managers.handle_callback(bot, update)

@handle_error
def cmd_catch_all(bot, update):
    chat_id = update.message.chat_id
    logger.info("In cmd_catch_all chat_id = %s", chat_id)
    cmd = update.message.text
    bot.send_message(
        chat_id=update.message.chat_id,
        text="מצטער, אני לא מכיר את הפקודה " + cmd
    )


def is_from_channel(update):
    if update.channel_post:
        if update.channel_post.chat.username == settings.TELEGRAM_CHANNEL:
            return True
    return False

@handle_error
def handle_reply(bot, update):
    from . import views
    logger.info("In handle_reply update = %s", ChatUtils.anonymize(update.to_json()))
    # note, we send here the full update object, not only the message
    # since for callback we need other members
    if is_from_channel(update):
        logger.info('skipping message from channel')
    else:
        views.handle_chat(ChatPlatform.TELEGRAM, update, bot=bot)


def setup_telegram_bot():
    bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
    updater: Updater = Updater(bot=bot)
    dispatcher: Dispatcher = updater.dispatcher
    # handle the /start command
    dispatcher.add_handler(CommandHandler('start', cmd_start))
    dispatcher.add_handler(CommandHandler('admin', cmd_admin))
    dispatcher.add_handler(CommandHandler('list', cmd_admin))
    dispatcher.add_handler(CallbackQueryHandler(handle_admin_callback, pattern=r'^admin_report:[a-z_]+:\d+$'))
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
import os

import telegram
from telegram.ext import CommandHandler, Updater, Filters, MessageHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
import logging

logging.basicConfig(format='[%(asctime)s - %(name)s - %(levelname)s] %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def get_token():
    with open("../train2/local_settings.py") as fh:
        for line in fh.readlines():
            if 'TELEGRAM_TOKEN' in line:
                token = line.partition("=")[2].strip()
                return token[1:-1]


TOKEN = get_token()


def start(bot, update):
    logger.info("In start")
    bot.send_message(
        chat_id=update.message.chat_id,
        text="I'm a bot, please talk to me!")


def caps(bot, update, args):
    logger.info("In caps args = %s bot = %s", args, id(bot))
    text_caps = ' '.join(args).upper()
    bot.send_message(
        chat_id=update.message.chat_id,
        text=text_caps)


def ibtns(bot, update):
    btns = [[InlineKeyboardButton(t, callback_data="ttt" + t) for t in ["yes", "no", "maybe"]]]
    reply_markup = InlineKeyboardMarkup(btns, one_time_keyboard=True)
    bot.send_message(
        chat_id=update.message.chat_id,
        text="please select",
        reply_markup=reply_markup)


def btns(bot, update):
    btns = [[KeyboardButton(t) for t in ["yes", "no", "maybe"]]]
    reply_markup = ReplyKeyboardMarkup(btns, one_time_keyboard=True)
    bot.send_message(
        chat_id=update.message.chat_id,
        text="please select",
        reply_markup=reply_markup)


def catch_all(bot, update):
    logger.info("In catch_all bot = %s", id(bot))
    cmd = update.message.text
    bot.send_message(
        chat_id=update.message.chat_id,
        text=f"I don't know what to do with this command {cmd}"
    )


def echo_back(bot, update):
    logger.info("In echo_back bot = %s", id(bot))
    bot.send_message(
        chat_id=update.message.chat_id,
        text=f"Thanks for sending: {update.message.text}"
    )


def handle_press(bot, update):
    logger.info("In handle_press")
    chat_id = update.callback_query.message.chat_id
    bot.send_message(
        chat_id=chat_id,
        text=f"Thanks for choosing {update.callback_query.data}"
    )
    logger.info(update.to_json())


def handle_atts(bot, update):
    print(update.message.to_dict())


def main():
    bot = telegram.Bot(token=TOKEN)
    logger.info("Bot = %s %s", bot.get_me(), id(bot))
    updater = Updater(bot=bot)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('caps', caps, pass_args=True))
    dispatcher.add_handler(CommandHandler('ibtns', ibtns))
    dispatcher.add_handler(CommandHandler('btns', btns))
    dispatcher.add_handler(MessageHandler(Filters.command, catch_all))
    dispatcher.add_handler(MessageHandler(Filters.text, echo_back))
    dispatcher.add_handler(MessageHandler(Filters.photo, handle_atts))
    dispatcher.add_handler(MessageHandler(Filters.video, handle_atts))
    dispatcher.add_handler(CallbackQueryHandler(handle_press))
    logger.info("Start polling")
    updater.start_polling()


if __name__ == '__main__':
    main()

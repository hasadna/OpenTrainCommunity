from collections import namedtuple
from typing import List

from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

from .consts import ChatPlatform

BotButton = namedtuple('BotButton', field_names=['title', 'payload'])
BotQuickReply = namedtuple('BotQuickReply', field_names=['title', 'payload'])


class BotWrapper:
    """
    wrapper class to provide same api for facebook and telegram
    """

    @classmethod
    def for_platform(cls, platform, bot):
        if platform == ChatPlatform.FACEBOOK:
            return FbBotWrapper(bot)
        if platform == ChatPlatform.TELEGRAM:
            return TgBotWrapper(bot)

    def __init__(self, bot):
        self.bot = bot


class FbBotWrapper(BotWrapper):
    def send_text_message(self, recipient_id, message):
        self.bot.send_text_message(recipient_id, message)

    def send_button_message(self, recipient_id, message, buttons: List[BotButton]):
        fb_buttons = [{
            'type': 'postback',
            'title': b.title,
            'payload': b.payload
        } for b in buttons]
        self.bot.send_button_message(recipient_id, message, fb_buttons)

    def send_quick_replies(self, recipient_id, message, quick_replies: List[BotQuickReply]):
        quick_replies_payload = [
            {
                'content_type': 'text',
                'title': r.title,
                'payload': r.payload,
            } for r in quick_replies
        ]
        message_payload = {
            'text': message,
            'quick_replies': quick_replies_payload
        }
        self.bot.send_message(recipient_id, message_payload)


class TgBotWrapper(BotWrapper):
    def send_text_message(self, chat_id, message):
        self.bot.send_message(
            chat_id=chat_id,
            text=message
        )

    def send_button_message(self, chat_id, message, buttons):
        buttons = [[
            InlineKeyboardButton(text=b.title, callback_data=b.payload)
            for b in buttons
        ]]
        self.bot.send_message(
            chat_id=chat_id,
            text=message,
            reply_markup=InlineKeyboardMarkup(buttons, one_time_keyboard=True),
        )

    def send_quick_replies(self, chat_id, message, quick_replies):
        """
        this is similar to send_button_message, but we put
        each on its own row
        """
        buttons = [
            [
                InlineKeyboardButton(text=r.title, callback_data=r.payload)
            ] for r in quick_replies
        ]
        self.bot.send_message(
            chat_id=chat_id,
            text=message,
            reply_markup=InlineKeyboardMarkup(buttons, one_time_keyboard=True),
        )





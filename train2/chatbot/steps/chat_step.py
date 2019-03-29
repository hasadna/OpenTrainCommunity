import abc
import json
import logging
import requests
from django.conf import settings

from pymessenger.bot import Bot

logger = logging.getLogger(__name__)


class ChatStep(abc.ABC):
    def __init__(self, session):
        self.session = session
        self.bot = Bot(settings.FB_PAGE_ACCESS_TOKEN)

    @staticmethod
    @abc.abstractmethod
    def get_name():
        raise NotImplementedError()

    @abc.abstractmethod
    def send_message(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def handle_user_response(self, handle_user_response):
        raise NotImplementedError()

    @staticmethod
    def _extract_text(messaging_event):
        text = messaging_event.get('message', {}).get('text', None)
        if text:
            text = text.strip()
        return text

    @staticmethod
    def _extract_selected_button(messaging_event):
        return messaging_event.get('postback', {}).get('payload', None)

    def _send_message(self, message):
        recipient_id = self.session.user_id
        logger.info("Sending message to %s: %s", recipient_id, message)

        self.bot.send_text_message(recipient_id, message)

    def _send_buttons(self, message, buttons):
        recipient_id = self.session.user_id
        logger.info("Sending buttons message to %s: %s", recipient_id, message)

        self.bot.send_button_message(recipient_id, message, buttons)

        # params = {
        #     "access_token": settings.FB_PAGE_ACCESS_TOKEN
        # }
        # headers = {
        #     "Content-Type": "application/json"
        # }
        # data = json.dumps({
        #     "recipient": {
        #         "id": recipient_id
        #     },
        #     "message": {
        #         "text": message
        #     }
        # })
        # r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
        # if r.status_code != 200:
        #     logger.info(r.status_code)
        #     logger.info(r.text)

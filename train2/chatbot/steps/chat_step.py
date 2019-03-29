import abc
import json
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class ChatStep(abc.ABC):
    def __init__(self, session):
        self.session = session

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

    def _send_message(self, message):
        recipient_id = self.session.user_id
        logger.info("sending message to %s: %s", recipient_id, message)

        params = {
            "access_token": settings.FB_PAGE_ACCESS_TOKEN
        }
        headers = {
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "text": message
            }
        })
        r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
        if r.status_code != 200:
            logger.info(r.status_code)
            logger.info(r.text)

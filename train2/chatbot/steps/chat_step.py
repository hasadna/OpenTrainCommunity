import abc
import logging
from django.conf import settings

from pymessenger.bot import Bot

logger = logging.getLogger(__name__)


class ChatStep(abc.ABC):
    MAX_ITEMS_FOR_SUGGESTIONS = 6
    MAX_ITEMS_FOR_BUTTONS = 4
    STORAGE_DATETIME_FORMAT = '%Y%m%d_%H%M'

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

    def _set_step_data(self, data, key=None):
        if key is None:
            key = self.get_name()
        self.session.steps_data[key] = data
        self.session.save()

    def _send_message(self, message):
        recipient_id = self.session.user_id
        logger.info("Sending message to %s: %s", recipient_id, message)

        self.bot.send_text_message(recipient_id, message)

    def _send_buttons(self, message, buttons):
        recipient_id = self.session.user_id
        logger.info("Sending buttons message to %s: %s", recipient_id, message)

        self.bot.send_button_message(recipient_id, message, buttons)

    def _send_suggestions(self, message, suggestions):
        recipient_id = self.session.user_id
        logger.info("Sending suggestions message to %s: %s", recipient_id, message)

        suggestions_payload = []
        for suggestion in suggestions:
            suggestions_payload.append({
                'content_type': 'text',
                'title': suggestion['text'],
                'payload': suggestion['payload'],
            })

        message_payload = {
            'text': message,
            'quick_replies': suggestions_payload
        }

        print(message_payload)
        self.bot.send_message(recipient_id, message_payload)

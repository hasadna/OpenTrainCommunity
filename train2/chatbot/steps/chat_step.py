import abc
import copy
import datetime
import logging

from chatbot.bot_wrapper import BotQuickReply
from chatbot.consts import ChatPlatform

logger = logging.getLogger(__name__)


class ChatStep(abc.ABC):
    MAX_ITEMS_FOR_SUGGESTIONS = 6
    MAX_ITEMS_FOR_BUTTONS = 4
    STORAGE_DATETIME_FORMAT = '%Y%m%d_%H%M'

    def __init__(self, *, session, bot_wrapper):
        self.bot_wrapper = bot_wrapper
        self.session = session

    @property
    def is_fb(self):
        return self.session.platform == ChatPlatform.FACEBOOK

    @property
    def is_tg(self):
        return self.session.platform == ChatPlatform.TELEGRAM

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

    def get_prev_result_key(self):
        return '{}:prev-result'.format(self.get_name())

    def _set_step_data(self, data, *, key=None):
        if key is None:
            key = self.get_name()
        self.session.steps_data[key] = data
        self.session.save()

    def _send_message(self, message):
        recipient_id = self.session.user_id
        logger.info("Sending message to %s: %s", recipient_id, message)

        self.bot_wrapper.send_text_message(recipient_id, message)

    def _send_buttons(self, message, buttons):
        recipient_id = self.session.user_id
        logger.info("Sending buttons message to %s: %s", recipient_id, message)

        resp = self.bot_wrapper.send_button_message(recipient_id, message, buttons)
        logger.info("Got %s", resp)

    def _send_suggestions(self, message, suggestions):
        recipient_id = self.session.user_id
        logger.info("Sending suggestions message to %s: %s", recipient_id, message)

        replies = [
            BotQuickReply(
                title=suggestion['text'],
                payload=suggestion['payload'],
            ) for suggestion in suggestions
        ]
        self.bot_wrapper.send_quick_replies(recipient_id, message, replies)

    def call_handle_user_response(self, data_wrapper):
        text = data_wrapper.extract_text()
        if text and "ביי" in text:
            return "terminate"
        return self.handle_user_response(data_wrapper)

    @staticmethod
    def _serialize_trip(trip):
        serialized_trip = copy.deepcopy(trip)
        serialized_trip['from']['departure_time'] = serialized_trip['from']['departure_time'].strftime('%H%M')
        serialized_trip['to']['departure_time'] = serialized_trip['to']['departure_time'].strftime('%H%M')
        return serialized_trip

    @staticmethod
    def _deserialize_trip(trip):
        deserialized_trip = copy.deepcopy(trip)
        deserialized_trip['from']['departure_time'] = datetime.datetime.strptime(deserialized_trip['from']['departure_time'], '%H%M').time()
        deserialized_trip['to']['departure_time'] = datetime.datetime.strptime(deserialized_trip['to']['departure_time'], '%H%M').time()
        return deserialized_trip

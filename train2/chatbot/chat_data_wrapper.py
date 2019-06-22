from .consts import ChatPlatform


class ChatDataWrapper:
    """
    wrapper class to provide same api for facebook and telegram
    """

    @classmethod
    def for_platform(cls, platform, data):
        if platform == ChatPlatform.FACEBOOK:
            return FbChatDataWrapper(data)
        if platform == ChatPlatform.TELEGRAM:
            return TgChatDataWrapper(data)

    def __init__(self, data):
        self.data = data

    def extract_text(self):
        t = self.do_extract_text()
        if t:
            return t.strip()
        return None


class FbChatDataWrapper(ChatDataWrapper):
    @property
    def messaging_event(self):
        return self.data

    def get_sender_id(self):
        return self.messaging_event['sender']['id']

    def do_extract_text(self):
        return self.messaging_event.get('message', {}).get('text', None)

    def extract_selected_button(self):
        return self.messaging_event.get('postback', {}).get('payload', None)

    def is_quick_reply(self):
        payload = self.messaging_event.get('message', {}).get('quick_reply', {}).get('payload', None)
        return payload is not None

    def extract_selected_quick_reply(self):
        return self.messaging_event.get('message', {}).get('quick_reply', {}).get('payload', None)


class TgChatDataWrapper(ChatDataWrapper):
    @property
    def update(self):
        return self.data

    @property
    def message(self):
        return self.update.message

    @property
    def callback_query(self):
        return self.update.callback_query

    def get_sender_id(self):
        if self.message:
            return self.message.chat_id
        if self.callback_query:
            return self.callback_query.message.chat_id

    def to_json(self):
        return self.update.to_dict()

    def do_extract_text(self):
        if self.message:
            return self.message.text

    def extract_selected_button(self):
        if self.callback_query:
            return self.callback_query.data

    def is_quick_reply(self):
        # we cannot distinguish between quick reply and buttons
        return self.callback_query is not None

    def extract_selected_quick_reply(self):
        if self.callback_query:
            return self.callback_query.data


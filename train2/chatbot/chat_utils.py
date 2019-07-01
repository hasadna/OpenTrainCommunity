import json

from . import constants


class ChatUtils:
    @staticmethod
    def get_response_to_step(session, step_name):
        for payload_str in reversed(session.payloads):
            payload = json.loads(payload_str)
            if payload['chat_step'] != step_name:
                continue
            return payload['messaging_event']

        return None

    @staticmethod
    def get_step_data(session, key):
        return session.steps_data.get(key)

    @staticmethod
    def anonymize(json_payload):
        """
        Removes First and last name from json payload
        :param json_payload:
        """
        if isinstance(json_payload, list):
            for item in json_payload:
                ChatUtils.anonymize(item)
        elif isinstance(json_payload, dict):
            for key in json_payload.keys():
                if key in ["first_name", "last_name"]:
                    json_payload[key] = constants.ANONYMOUS
                else:
                    v = json_payload[key]
                    ChatUtils.anonymize(v)

        return json_payload

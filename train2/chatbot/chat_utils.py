import json


class ChatUtils:
    @staticmethod
    def get_response_to_step(session, step_name):
        for payload_str in reversed(session.payloads):
            payload = json.loads(payload_str)
            if payload['chat_step'] != step_name:
                continue
            return payload['messaging_event']

        return None

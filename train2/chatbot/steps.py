from django.conf import settings
import requests
import logging
import json

logger = logging.getLogger(__name__)


def step_welcome(session):
    welcome_msg = '''
    הי! אני בוט שמאפשר לדווח על ביטול רכבות
    האם מדובר על רכבת סביב שעה מעכשיו?
    '''
    send_message(session.user_id, welcome_msg)


def send_message(recipient_id, message_text):
        logger.info("sending message to %s: %s", recipient_id, message_text)
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
                "text": message_text
            }
        })
        r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
        if r.status_code != 200:
            logger.info(r.status_code)
            logger.info(r.text)

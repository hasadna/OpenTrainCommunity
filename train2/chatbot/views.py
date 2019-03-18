import json

import requests
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.views import View
import logging

from . import models


logger = logging.getLogger(__name__)


class HookView(View):
    def get(self, request, *args, **kwargs):
        logger.info("GET=%s", request.GET)
        mode = request.GET.get('hub.mode')
        if mode == "subscribe" and request.GET.get("hub.challenge"):
            if not request.GET.get("hub.verify_token") == settings.FB_VERIFY_TOKEN:
                raise PermissionDenied("Verification token mismatch")
        challenge = request.GET.get('hub.challenge', '??')
        return HttpResponse(challenge, status=200)

    def post(self, request, *args, **kwargs):
        # endpoint for processing incoming messaging events
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)
        logger.info("data = %s", json.dumps(data, indent=4, sort_keys=True))
        if data["object"] == "page":
            for entry in data["entry"]:
                for messaging_event in entry["messaging"]:
                    handle_messaging_event(messaging_event)

        return HttpResponse("ok", status=200)


def handle_messaging_event(messaging_event):
    if 'message' in messaging_event:
        sender_id = messaging_event['sender']['id']
        session = get_session(sender_id)
        session.payloads.append(messaging_event)
        session.save()
        globals()[f'handle_step_{session.step}'](session)


def get_session(sender_id):
    return models.ChatSession.objects.get_or_create(
        user_id=sender_id
    )


def handle_step_welcome(session):
    welcome_msg = '''
    שלום רב, אני בוט שמאפשר לדווח על ביטול רכבות
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


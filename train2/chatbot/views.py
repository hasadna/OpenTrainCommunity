import json

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.views import View
import logging

from . import models
from . import steps


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
    if 'message' not in messaging_event:
        return

    message = messaging_event['message']['text'].strip()
    sender_id = messaging_event['sender']['id']

    session = get_session(sender_id)
    payload = json.dumps({
        'messaging_event': messaging_event,
        'chat_step': session.current_step
    })
    session.payloads.append(payload)

    current_step_name = session.current_step
    step = steps.get_step(current_step_name)(session)

    next_step_name = step.handle_user_response(message)
    session.current_step = next_step_name
    session.save()
    next_step = steps.get_step(next_step_name)(session)

    next_step.send_message()


def get_session(sender_id):
    return models.ChatSession.objects.get_or_create(
        user_id=sender_id
    )[0]

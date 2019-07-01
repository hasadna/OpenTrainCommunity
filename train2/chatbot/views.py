import json
import logging

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.views import View
from pymessenger.bot import Bot

from chatbot import chat_utils
from common import slack_utils
from . import models, steps
from .bot_wrapper import BotWrapper
from .chat_data_wrapper import ChatDataWrapper
from .consts import ChatPlatform

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
                    try:
                        handle_fb_messaging_event(messaging_event)
                    except Exception as ex:
                        logger.exception("error in facebook handling")
                        slack_utils.send_error(f'error in call to FB: {ex}')
        return HttpResponse("ok", status=200)


def handle_fb_messaging_event(messaging_event):
    if "policy-enforcement" in messaging_event:
        handle_policy_enforcement(messaging_event)
        return

    if 'message' not in messaging_event and 'postback' not in messaging_event:
        return

    handle_chat(
        ChatPlatform.FACEBOOK,
        messaging_event,
        bot=Bot(settings.FB_PAGE_ACCESS_TOKEN))


def handle_chat(platform, data, bot):
    data_wrapper = ChatDataWrapper.for_platform(platform, data)
    sender_id = data_wrapper.get_sender_id()
    bot_wrapper = BotWrapper.for_platform(platform, bot)
    session = models.ChatSession.objects.get_session(platform, sender_id)

    payload = {
        'payload': chat_utils.ChatUtils.anonymize(data_wrapper.to_json()),
        'chat_step': session.current_step
    }
    session.payloads.append(payload)

    current_step_name = session.current_step
    step = steps.get_step(current_step_name)(session=session, bot_wrapper=bot_wrapper)

    next_step_name = step.call_handle_user_response(
        data_wrapper
    )
    session.current_step = next_step_name
    session.save()
    next_step = steps.get_step(next_step_name)(session=session, bot_wrapper=bot_wrapper)

    next_step.send_message()


def handle_policy_enforcement(messaging_event):
    pretty_event = json.dumps(messaging_event, indent=4)
    slack_utils.send_error(f'Received a facebook policy enforcement event: {pretty_event}')

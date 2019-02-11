import json

import requests
from django.conf import settings
from django.http import HttpResponse
from django.views import View
import logging

logger = logging.getLogger(__name__)


class HookView(View):
    def get(self, request, *args, **kwargs):
        logger.info("GET=%s", request.GET)
        challenge = request.GET.get('hub.challenge','??')
        return HttpResponse(challenge, status=200)

    def post(self, request, *args, **kwargs):
        # endpoint for processing incoming messaging events
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)
        logger.info("data = %s", json.dumps(data, indent=4, sort_keys=True))
        if data["object"] == "page":
            for entry in data["entry"]:
                for messaging_event in entry["messaging"]:

                    if messaging_event.get("message"):  # someone sent us a message
                        # the facebook ID of the person sending you the message
                        sender_id = messaging_event["sender"]["id"]
                        # the recipient's ID, which should be your page's facebook ID
                        recipient_id = messaging_event["recipient"]["id"]
                        # the message's text
                        message_text = messaging_event["message"]["text"]
                        send_message(sender_id, "roger that!")
                    # delivery confirmation
                    if messaging_event.get("delivery"):
                        pass
                    # optin confirmation
                    if messaging_event.get("optin"):
                        pass
                    # user clicked/tapped "postback" button in earlier message
                    if messaging_event.get("postback"):
                        pass
        return HttpResponse("ok", status=200)


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


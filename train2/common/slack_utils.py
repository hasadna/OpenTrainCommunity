import logging
import requests
import json
from django.conf import settings


logger = logging.getLogger(__name__)


def send_message(msg):
    url = settings.SLACK_URL
    payload = {
        'channel': '#opentrain',
        'username': 'webhookbot',
        'text': f'[SYSTEM MESSAGE] {msg}',
        'icon_emoji': ':train2:'
    }
    return requests.post(url, data={'payload': json.dumps(payload)})



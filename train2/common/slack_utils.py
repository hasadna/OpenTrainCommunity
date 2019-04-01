import logging
import requests
import json
from django.conf import settings


logger = logging.getLogger(__name__)


def send_error(msg):
    send_message('ERROR', msg)


def send_info(msg):
    send_message('INFO', msg)


def send_message(level, msg):
    url = settings.SLACK_URL
    payload = {
        'channel': '#opentrain',
        'username': 'webhookbot',
        'text': f'[{level}] {msg}',
        'icon_emoji': ':train2:'
    }
    return requests.post(url, data={'payload': json.dumps(payload)})



import logging
from collections import namedtuple
import telegram
from django.conf import settings

from chatbot.consts import ChatPlatform

logger = logging.getLogger(__name__)


Attachment = namedtuple('Attachment', field_names=['type', 'url'])


def collect_attachments_from_payload(session, payload):
    if session.platform == ChatPlatform.FACEBOOK:
        return _collect_attachments_from_payload_fb(payload)
    elif session.platform == ChatPlatform.TELEGRAM:
        return _collect_attachments_from_payload_tg(payload)


def _collect_attachments_from_payload_fb(payload):
    m = payload.get('message', {})
    atts = m.get('attachments', [])
    return [
        Attachment(url=att['payload']['url'], type=att['type'])
        for att in atts
    ]


def _collect_attachments_from_payload_tg(payload):
    m = payload.get('message', {})
    result = []
    bot = telegram.Bot(settings.TELEGRAM_TOKEN)
    try:
        if 'photo' in m and m['photo']:
            p = max(m['photo'], key=lambda p1: p1['width'])
            file_id = p['file_id']
            result.append(
                Attachment(
                    type='image',
                    url=bot.get_file(file_id).file_path
                )
            )
        if 'video' in m:
            v = m['video']
            file_id = v['file_id']
            result.append(
                Attachment(
                    type='video',
                    url=bot.get_file(file_id).file_path
                )
            )
    except telegram.error.BadRequest as ex:
        logger.error("Failed to extract message: %s", ex)
    return result

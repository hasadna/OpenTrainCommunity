from django.conf import settings
import json
import logging
import requests

from . import welcome_step
from . import train_date_and_time_step
from . import source_station_step
from . import destination_station_step
from . import goodbye_step

logger = logging.getLogger(__name__)


STEPS = {
    'welcome': welcome_step.WelcomeStep,
    'train_date_and_time': train_date_and_time_step.TrainDateAndTimeStep,
    'source_station': source_station_step.SourceStationStep,
    'destination_station': destination_station_step.DestinationStationStep,
    'goodbye': goodbye_step.GoodbyeStep,
}


def get_step(step_name):
    return STEPS[step_name]


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

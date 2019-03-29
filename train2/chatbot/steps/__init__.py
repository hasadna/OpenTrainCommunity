from django.conf import settings
import json
import logging
import requests

from . import initial_step
from . import welcome_step
from . import train_date_and_time_step
from . import source_station_step
from . import destination_station_step
from . import goodbye_step

logger = logging.getLogger(__name__)


STEPS = {
    'initial': initial_step.InitialStep,
    'welcome': welcome_step.WelcomeStep,
    'train_date_and_time': train_date_and_time_step.TrainDateAndTimeStep,
    'source_station': source_station_step.SourceStationStep,
    'destination_station': destination_station_step.DestinationStationStep,
    'goodbye': goodbye_step.GoodbyeStep,
}


def get_step(step_name):
    return STEPS[step_name]

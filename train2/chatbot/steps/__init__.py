import logging

from chatbot.steps import confirm_retry_step
from . import accepted_step
from . import destination_station_step
from . import initial_step
from . import more_media_step
from . import restart_step
from . import select_train_line_step
from . import source_station_step
from . import terminate_step
from . import train_date_and_time_step
from . import train_time_approx_now_step
from . import welcome_step

logger = logging.getLogger(__name__)


STEPS = {
    'initial': initial_step.InitialStep,
    'welcome': welcome_step.WelcomeStep,
    'train_time_approx_now': train_time_approx_now_step.TrainTimeApproxNowStep,
    'train_date_and_time': train_date_and_time_step.TrainDateAndTimeStep,
    'source_station': source_station_step.SourceStationStep,
    'destination_station': destination_station_step.DestinationStationStep,
    'select_train_line': select_train_line_step.SelectTrainLineStep,
    'accepted': accepted_step.AcceptedStep,
    'restart': restart_step.RestartStep,
    'terminate': terminate_step.TerminateStep,
    'more_media': more_media_step.MoreMediaStep,
    'confirm_retry': confirm_retry_step.ConfirmRetryStep
}


def get_step(step_name):
    return STEPS[step_name]

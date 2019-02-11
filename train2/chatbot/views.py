from django.http import HttpResponse
from django.views import View
import logging

logger = logging.getLogger(__name__)


class HookView(View):
    def get(self, request, *args, **kwargs):
        logger.info("GET=%s", request.GET)
        challenge = request.GET.get('hub.challenge','??')
        return HttpResponse(challenge, status=200)


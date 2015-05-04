from django.middleware.common import CommonMiddleware
import logging
from data import errors
from django.http import HttpResponse
import json

class OpenTrainMiddleware(CommonMiddleware):
    def process_exception(self,request,exception):
        if isinstance(exception,errors.TrainError):
            content = {'details':unicode(exception),
                       'kind': exception.__class__.__name__}
            return HttpResponse(status=400,content_type='application/json',content=json.dumps(content))
        error_logger = logging.getLogger('errors')
        error_logger.exception('exception in %s %s' % (request.method,request.path))


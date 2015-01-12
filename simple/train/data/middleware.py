from django.middleware.common import CommonMiddleware
import logging
class OpenTrainMiddleware(CommonMiddleware):
    def process_exception(self,request,exception):
        error_logger = logging.getLogger('errors')
        error_logger.exception('exception in %s %s' % (request.method,request.path))


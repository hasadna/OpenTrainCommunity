try:
    import redis

    CACHE_ENABLED = True
    CLIENT = redis.StrictRedis()
    TTL = 30 * 24 * 60 * 60

except ImportError:
    CACHE_ENABLED = False

print '********* cache_enabled = %s' % CACHE_ENABLED
from django.http import HttpResponse


def _build_key(req):
    return req.get_full_path()


def cacheit(func):
    def wrap(req, *args, **kwargs):
        if CACHE_ENABLED:
            key = _build_key(req)
            cc = CLIENT.get(key)
            if cc:
                print 'Return cached version of %s' % req.get_full_path()
                return HttpResponse(status=200, content=cc, content_type='application/json')
        result = func(req, *args, **kwargs)
        if CACHE_ENABLED:
            CLIENT.setex(key, TTL, result.content)
        return result

    return wrap


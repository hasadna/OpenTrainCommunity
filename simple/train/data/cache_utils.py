try:
    import redis

    CACHE_ENABLED = True
    CLIENT = redis.StrictRedis()
    TTL = 30 * 24 * 60 * 60

except ImportError:
    CACHE_ENABLED = False

#print '********* cache_enabled = %s' % CACHE_ENABLED
from django.http import HttpResponse
import json

def invalidate_cache():
    if CACHE_ENABLED:
        CLIENT.flushdb()
        print 'Flushed db'

def _build_key(req):
    return req.get_full_path()


def cachereq(func):
    """
    decorator to cache request call, returns HTTP response
    """
    def wrap(req, *args, **kwargs):
        use_cache = req.GET.get('no_cache',None) != '1' and CACHE_ENABLED
        if use_cache:
            key = _build_key(req)
            cc = CLIENT.get(key)
            if cc:
                #print 'Return cached version of %s' % req.get_full_path()
                return HttpResponse(status=200, content=cc, content_type='application/json')
        result = func(req, *args, **kwargs)
        if use_cache:
            CLIENT.setex(key, TTL, result.content)
        return result

    return wrap

def cache_obj_method(func):
    """
    decorator for function that returns json-able object
    """
    def wrap(obj, *args, **kwargs):
        key = '%s:%s' % (func.__name__ ,obj.id)
        cc = CLIENT.get(key)
        if cc:
            return json.loads(cc)
        result = func(obj, *args, **kwargs)
        CLIENT.setex(key, TTL, json.dumps(result))
        return result

    return wrap


def cache_result(func):
    """
    decorator for function that returns json-able object
    """
    def wrap():
        key = '%s' % (func.__name__)
        cc = CLIENT.get(key)
        if cc:
            return json.loads(cc)
        result = func()
        CLIENT.setex(key, TTL, json.dumps(result))
        return result
    return wrap
try:
    import redis
    cache_enabled = True
    CLIENT = redis.StrictRedis()
    TTL = 30*24*60*60

except ImportError:
    cache_enabled = False

print '********* cache_enabled = %s' % cache_enabled
from django.http import HttpResponse

def _build_key(req):
    return req.get_full_path()

def cacheit(func):
    def wrap(req,*args,**kwargs):
        if cache_enabled:
            key = _build_key(req)
            cc = get_cache(key)
            if cc:
                print 'Return cached version of %s' % req.get_full_path()
                return HttpResponse(status=200,content=cc,content_type='application/json')
        result = func(req,*args,**kwargs)
        if cache_enabled:
            set_cache(key,result.content)
        return result
    return wrap

def get_cache(key):
    return CLIENT.get(key)

def set_cache(key,content):
    return CLIENT.setex(key,TTL,content)


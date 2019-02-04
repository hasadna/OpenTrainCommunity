from django.http import HttpResponse
from django.views import View


class HelloWorldView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('hello world', status=200)


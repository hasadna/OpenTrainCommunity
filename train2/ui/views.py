# Create your views here.
from django.views.generic import TemplateView


class RouteExplorer(TemplateView):
    template_name = 'ui/RouteExplorer.html'



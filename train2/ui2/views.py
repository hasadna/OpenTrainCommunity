# Create your views here.
from django.views.generic import TemplateView


class AppView(TemplateView):
    template_name = 'ui2/app.html'



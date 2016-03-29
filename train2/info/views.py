from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.views.generic import TemplateView, FormView
from django import forms

import data.models


class RoutesForm(forms.Form):
    route_id = forms.IntegerField()
    old_or_new = forms.ChoiceField(label='convert from',
                                   choices=(
        ('old','old site (otrain.org)'),
        ('new', 'new site (next.otrain.org')))


class RoutesView(FormView):
    form_class = RoutesForm
    template_name = 'info/routes.html'

    def get_context_data(self, **kwargs):
        d = super().get_context_data(**kwargs)
        route_id = self.request.GET.get('route_id')
        is_new = self.request.GET.get('is_new')
        if route_id and is_new:
            d['has_result'] = True
            d['old_route_id'] = 123
            d['new_route_id'] = 456
            d['stops'] = data.models.Stop.objects.all()[0:4]
        return d

    def form_valid(self, form):
        is_new = form.cleaned_data['old_or_new'] == 'old'
        route_id = form.cleaned_data['route_id']
        self.success_url = '{}?is_new={}&route_id={}'.format(reverse('info:routes'),
                                                route_id,
                                                1 if is_new else 0)
        return super().form_valid(form)



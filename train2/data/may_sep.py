# may-sep analysis
import datetime

from django.db.models.functions import ExtractHour

from data.models import Sample


def by_hour(hours):
    qs_ns = Sample.objects.filter(
            valid=True).filter(
            is_source=False,trip__date__gte=datetime.date(2017,5,1)).annotate(
            h=ExtractHour('exp_arrival')).filter(h__in=hours)
    qs_ns_late = qs_ns.filter(exp_arrival__gte=300).count()
    qs_s = Sample.objects.filter(
            valid=True).filter(
            is_source=False,trip__date__gte=datetime.date(2017,5,1)).annotate(
            h=ExtractHour('exp_departure')).filter(h__in=hours)
    qs_s_late = qs_s.filter(exp_departure__gte=300).count()
    print('hours = %s' % (hours))
    print('non source = %d / %d => %.2f' % (qs_ns_late.count(), qs_ns.count(), 100 * qs_ns_late.count() / qs_ns.count()))
    print('source = %d / %d => %.2f' % (qs_s_late.count(), qs_s_late.count(), 100 * qs_s_late.count() / qs_s.count()))


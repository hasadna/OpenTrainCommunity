import logging
import datetime
from django.utils import timezone
from django.db import connection

from data.models import Trip

logger = logging.getLogger(__name__)

row_sql = '''
update data_trip as dt
set x_max2_delay_arrival = sq.m2,
  x_max_delay_arrival = sq.m1,
  x_avg_delay_arrival = sq.a,
  x_cache_version = 1
from
(
  SELECT
    s.trip_id as tid,
    avg(s.delay_arrival) as a,
    max(s.delay_arrival) as m1,
    (array_agg(s.delay_arrival
    ORDER BY s.delay_arrival DESC)) [2] AS m2
  FROM
    data_sample AS s
  where s.valid = True and s.delay_arrival is not null
  group by s.trip_id
) as sq
where dt.id = sq.tid and dt.date >= %s and dt.date < %s and dt.valid = True and dt.x_cache_version < 1;
'''


def  update_range(date1, date2):
    with connection.cursor() as c:
        c.execute(row_sql, [date1, date2])
        res = c.rowcount
        logger.info("updating range %s to %s => %s", date1, date2, res)


def update_all():
    # we just run in batches of 30 days
    today = timezone.now().date()
    try:
        date1 = Trip.objects.filter(valid=True, x_cache_version__lt=1).earliest('date').date - datetime.timedelta(days=3)
    except Trip.DoesNotExist:
        logger.info("All updated!!!")
        return
    while date1 <= today:
        date2 = date1 + datetime.timedelta(days=30)
        update_range(date1, date2)
        date1 = date2






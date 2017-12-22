# return trip_id, max, max2, avg delay for all samples
update data_trip

select s.trip_id,
  avg(s.delay_arrival) as a,
  max(s.delay_arrival) as m1,
  (array_agg(s.delay_arrival order by s.delay_arrival desc))[2] as m2
   from data_sample as s
   where s.valid = True and s.delay_arrival is not null
   group by s.trip_id order by m1 desc limit 1000 ;

# same but using join

select
  t.date,
  t.id,
  avg(s.delay_arrival) as a,
  max(s.delay_arrival) as m1,
  (array_agg(s.delay_arrival order by s.delay_arrival desc))[2] as m2
from
  data_sample as s join
  data_trip as t
  on s.trip_id = t.id
where s.valid = True and s.delay_arrival is not null and t.date > '2017-10-1'
  group by t.id order by m1 desc;

update data_trip
set x_max_delay_arrival = sq.m1,
    x_max2_delay_arrival = sq.m2,
    x_avg_delay_arrival = sq.a
from data_trip as dt JOIN
  (select
  t.id as tid,
  avg(s.delay_arrival) as a,
  max(s.delay_arrival) as m1,
  (array_agg(s.delay_arrival order by s.delay_arrival desc))[2] as m2
from
  data_sample as s join
  data_trip as t
  on s.trip_id = t.id
where s.valid = True and s.delay_arrival is not null and t.date >= '2017-10-29'
  group by t.id order by m1 desc) as sq
  on sq.tid = dt.id;


select
  t.date,
  t.id,
  t.x_max_delay_arrival,
  max(s.delay_arrival) as m1,
  t.x_max2_delay_arrival,
  (array_agg(s.delay_arrival order by s.delay_arrival desc))[2] as m2,
  t.x_avg_delay_arrival,
  avg(s.delay_arrival) as a
from
  data_sample as s join
  data_trip as t
  on s.trip_id = t.id
where s.valid = True and s.delay_arrival is not null and t.date > '2017-10-30'
  group by t.id order by m1 desc;


update data_trip as dt
set x_max2_delay_arrival = sq.m2,
  x_max_delay_arrival = sq.m1,
  x_avg_delay_arrival = sq.a
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
where dt.id = sq.tid and dt.date > '2017-10-25'


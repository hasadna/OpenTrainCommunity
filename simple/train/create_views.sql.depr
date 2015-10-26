--DROP MATERIALIZED VIEW if exists data_sample_with_hour;
--CREATE MATERIALIZED VIEW data_sample_with_hour AS
--       SELECT s.trip_id AS trip_id,
--       s.stop_id AS stop_id,
--       extract(hour FROM timezone('Asia/Jerusalem',s.exp_departure)) AS hour_pg,
--       extract(dow FROM t.start_date) AS week_day_pg
--       FROM data_sample AS s JOIN data_trip AS t
--       ON s.trip_id = t.id;

DROP MATERIALIZED VIEW if exists trip_with_hour;
CREATE MATERIALIZED VIEW trip_with_hour AS
       SELECT t.*,
       extract(hour FROM timezone('Asia/Jerusalem',s.exp_departure)) AS hour_pg,
       extract(dow FROM t.start_date) AS week_day_pg
       FROM data_sample AS s JOIN data_trip AS t
       ON s.trip_id = t.id
       WHERE s.is_first;



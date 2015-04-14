DROP MATERIALIZED VIEW if exists data_sample_with_hour;
CREATE MATERIALIZED VIEW data_sample_with_hour AS select trip_id,stop_id,extract(hour from timezone('Asia/Jerusalem',exp_departure)) as hour_pg from data_sample;


DROP VIEW IF EXISTS delays;
DROP VIEW IF EXISTS last_delay_view;
DROP VIEW IF EXISTS max_delay_with_stop_view;
DROP VIEW IF EXISTS max_delay_view ;

CREATE VIEW last_delay_view as
select S.trip_id,S.stop_id,S.delay_arrival as last_delay from data_sample as S 
       where S.is_last and S.valid;


CREATE VIEW max_delay_view as 
select S.trip_id,max(delay_arrival) as max_delay from data_trip as T join data_sample as S on T.id = S.trip_id where S.valid and T.valid group by S.trip_id;

CREATE VIEW max_delay_with_stop_view as 
select S.trip_id,S.stop_id,M.max_delay from max_delay_view as M,data_sample as S where S.trip_id = M.trip_id and S.delay_arrival = M.max_delay;

CREATE VIEW delays as 
select M.trip_id ,M.max_delay,L.last_delay,M.max_delay - L.last_delay as delay_offset from max_delay_view as M join last_delay_view as L on M.trip_id = L.trip_id;




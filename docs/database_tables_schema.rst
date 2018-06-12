Database tables schema
========


==============================  					=============================================
data_sample	  																		represents arrival, departure at a  station, time as part of a trip
==============================  					=============================================
id	  																		automatic ID by DB
index	  																	the index of the stop in the trip [#]_
gtfs_stop_id	  													the station GTFS id
stop_id	  																the station id, a foreign key to the data_stops table
valid	  																	data sanity check
invalid_reason	  												description of invalid reason, if invalid
is_source	  															whether it the first passengers stop (there may be non-passenger stops before)
is_dest	  																whether it the last passengers stop
actual_arrival	  												time of arrival
actual_arrival_fixed	  												is field actual_arrival missing, if so - used exp_arrival
exp_arrival	  														the planned time
delay_arrival	  													the delta of actual_arrival – exp_arrival
actual_departure	  											time of departure
actual_departure_fixed	  												is field actual_departure missing, if so - used exp_departure
exp_departure	  													planned departure
delay_departure	  												the delta of actual_departure – exp_departure
filename	  															source of data (for debugging purposes)
line_number	  														the line in that file (for debugging purposes)
sheet_idx	  																the sheet in that file (for debugging purposes)
trip_id	  																the id of the trip <train, date> (train = route id)
==============================  					=============================================
.. [#] Note that there are gaps in the indexes since the original indexing includes operational stops.
|
|

==============================  					=============================================
data_trip	  																		collection of samples representing a unique trip from source to destination
==============================  					=============================================
id	  																		the trip id, a non generated primary key (timestamp & train nr)
train_num   															train num as given by the train
date   															date of trip
valid	  																	data sanity check
invalid_reason	  												description of invalid reason, if invalid
x_week_day_local	  												day of week (0 to 6) (first sample in the trip)
x_hour_local	  												expected hour of departure (first sample in the trip)
route_id  																foreign key to the route table
x_avg_delay_arrival	  												average delay over all samples in the trip
x_cache_version	  												cache version being used for this table, used for table updates
x_max2_delay_arrival	  												second largest delay among the route's samples
x_max_delay_arrival	  												largest delay among the route's samples
x_before_last_delay_arrival	  												delay at route's second to last sample
x_last_delay_arrival	  												delay at route's last sample

==============================  					=============================================
.. [#] Service is a collection of trips of the same route and same hours. E.g. all trains from Beer Sheva to Nahariya at 8 am.
|
|

==============================  					=============================================
data_route	  																		list of stops for a repeating route
==============================  					=============================================
id	  																		automatic ID by DB
stop_ids   																json list of stop ids
==============================  					=============================================
|
|

==============================  					=============================================
data_stop	  																		static info about stops in the rail network
==============================  					=============================================
id	  																		automatic ID by DB
gtfs_stop_id	  																		gtfs (General Transit Feed Specification) station id
english	  																		english name
hebrews	  																		hebrew names (json list)
lat	  																		latitude
lon	  																		longitude
==============================  					=============================================

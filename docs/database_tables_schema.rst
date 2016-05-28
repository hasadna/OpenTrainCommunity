Database tables schema
========


==============================  					=============================================
data_sample
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
exp_arrival	  														the planned time
delay_arrival	  													the delta of actual_arrival – exp_arrival
actual_departure	  											time of departure
exp_departure	  													planned departure
delay_departure	  												the delta of actual_departure – exp_departure
filename	  															source of data (for debugging purposes)
line_number	  														the line in that file (for debugging purposes)
trip_id	  																the id of the trip <train, date> (train = route id)
==============================  					=============================================
.. [#] Note that there are gaps in the indexes since the original indexing includes operational stops.
|
|

==============================  					=============================================
data_trip
==============================  					=============================================
id	  																		the trip id, a non generated primary key (timestamp & train nr)
train_num   															train num as given by the train
route_id  																foreign key to the route table
service_id   															foreign key to the service table [#]_
==============================  					=============================================
.. [#] Service is a collection of trips of the same route and same hours. E.g. all trains from Beer Sheva to Nahariya at 8 am.
|
|

==============================  					=============================================
data_route
==============================  					=============================================
route	  																	a list of all stops
stop_ids   																json list of stop ids
==============================  					=============================================

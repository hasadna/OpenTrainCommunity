API for Android
================

Get all networks (GET): 
http://gtfs.otrain.org/api/data/bssids

Add new network (POST): 
http://gtfs.otrain.org/api/data/bssids/add/ ::

  {
    bssid: "ab:cd:ef:gh:ij:kl
    name: "Hashalom"
    stop_id: “37350”
  }

Admin interface for manual update: 
http://gtfs.otrain.org/admin/

Stop list: 
http://gtfs.otrain.org/api/gtfs/stops/?format=json

Today’s gtfs trips: 
http://gtfs.otrain.org/api/gtfs/trips/date/today/?format=json

Specific day’s gtfs trips: 
http://gtfs.otrain.org/api/gtfs/trips/date/2015-09-10/?format=json

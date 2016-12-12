
Our data
========

We take the raw Israel Railways data we receive and do minimal processing - mainly structuring it and marking invalid data as such. Each data point in our database has a pointer to a specific line in one of the raw files we've received from Israel Railways. That way, if and when some question arises about the data, we can always pinpoint the exact source of that data.

- Raw Excel data received from Israel Railways:
 - http://otrain.org/files/xl-feb-2016/times/ 
 - http://otrain.org/files/xl-april-2016/

- Dump of our database: http://otrain.org/files/dumps

- Our database in csv format: http://otrain.org/files/dumps-csv


Adding new data
---------------
- Put the data in ~/public_html/files/ on the server in an appropriate folder (follow the standard there).
- While under 'workon train2' virtualenv and in the ~/work/OpenTrainCommunity/train2 folder, run:
::

 python manage.py parsexl /home/opentrain/public_html/files/xl-2016-nov/xl-2016-nov.xlsx

Make sure to change to your excel file. You should get something similar to::

[28/11/2016 17:30:20] INFO [utils_2015:137] Creating routes
[28/11/2016 17:31:14] INFO [utils_2015:141] # of valid trips = 9592
[28/11/2016 17:31:14] INFO [utils_2015:142] # of invalid trips = 136
[28/11/2016 17:31:14] INFO [utils_2015:146] Reason: sample has different planned and stopped count = 29
[28/11/2016 17:31:14] INFO [utils_2015:146] Reason: missing actual_arrival count = 27
[28/11/2016 17:31:14] INFO [utils_2015:146] Reason: missing actual_departure count = 57
[28/11/2016 17:31:14] INFO [utils_2015:146] Reason: first stop is not is_source count = 21
[28/11/2016 17:31:14] INFO [utils_2015:146] Reason: last stop is not is_dest count = 2

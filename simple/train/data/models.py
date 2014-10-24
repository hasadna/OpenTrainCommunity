from django.db import models
from django.conf import settings
from djorm_pgarray.fields import IntegerArrayField


class Sample(models.Model):
    """
    README:
    =======
    this model represents one line in the input
    Note that lines were dumped to DB after groups to trips and after several checks
    Each line belong to trip, and in each day the combination of train_num,start_date should be unique
    The trip_id is string combination of train num and start date
    If there was eny error in the trip then all its samples are marked as valid = False, you can filter it out
    The exp arrival and exp departure should be None only in first/last stop respectively.
    The actual arrival and actual departure should be None in first/last stop respectively, but can be also None if the sample is missing
    If there is no actual arrival or actual departure, then the delay is None also.

    Note that there are samples for real stops and for midpoints in the way, as given by the train. Non real stops have is_real_stop = False
    and their name is prefixed with -

    """
    trip_name = models.CharField(max_length=30,db_index=True) # generated id for the given trip (combination of train num and date)
    train_num = models.IntegerField(db_index=True) # the train num as given in the text files
    start_date = models.DateField(db_index=True) # the start date of the trip (note that trip can be spanned over two days)
    index = models.IntegerField() # the index of the stop in the trip (0 based)
    stop_id = models.IntegerField(db_index=True) # the stop id
    stop_name = models.CharField(max_length=100) # the stop name in english - not formal name, if this is not real stop will be prefixed with -
    is_real_stop = models.BooleanField(default=False) # true is this is real stop
    valid = models.BooleanField(default=False,db_index=True) # true if this is stop in valid trip (e.g. with no errros)
    is_first = models.BooleanField(default=False) # true if this is the first stop of the trip (index = 0)
    is_last = models.BooleanField(default=False) # true if this is the last stop
    actual_arrival = models.DateTimeField(blank=True,null=True) # actual arrival time with tz, will be None if there is no such
    exp_arrival = models.DateTimeField(blank=True,null=True) # exp arrival time with tz, will be None if this is the first stop
    delay_arrival = models.FloatField(blank=True,null=True) # the delay in the arrival in seconds
    actual_departure = models.DateTimeField(blank=True,null=True) # actual depart time with tz, will be None if there is no such
    exp_departure = models.DateTimeField(blank=True,null=True) # exp depart time with tz, will be None if this is the last stop
    delay_departure = models.FloatField(blank=True,null=True) # the delay in the departure in seconds
    data_file = models.CharField(max_length=100) # the name of the data file (text file)
    data_file_line = models.IntegerField() # the line number in the data file (text file)
    data_file_link = models.URLField(max_length=200) # link to show the snippet of the text file in browser
    trip = models.ForeignKey('Trip',blank=True,null=True)

    class Meta:
        unique_together = ('trip_name','index')

class Trip(models.Model):
    id = models.CharField(primary_key=True,max_length=30,db_index=True,unique=True)
    train_num = models.IntegerField(db_index=True)
    start_date = models.DateField(db_index=True)
    valid = models.BooleanField(default=False)
    stop_ids = IntegerArrayField()



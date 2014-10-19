from django.db import models
from django.conf import settings

class Sample(models.Model):
    trip_id = models.CharField(max_length=30,db_index=True)
    train_num = models.IntegerField(db_index=True)
    start_date = models.DateField(db_index=True)
    index = models.IntegerField()
    stop_id = models.IntegerField(db_index=True)
    stop_name = models.CharField(max_length=100)
    is_real_stop = models.BooleanField()
    valid = models.BooleanField(db_index=True)
    is_first = models.BooleanField()
    is_last = models.BooleanField()
    actual_arrival = models.DateTimeField(blank=True,null=True)
    exp_arrival = models.DateTimeField(blank=True,null=True)
    delay_arrival = models.FloatField(blank=True,null=True)
    actual_departure = models.DateTimeField(blank=True,null=True)
    exp_departure = models.DateTimeField(blank=True,null=True)
    delay_departure = models.FloatField(blank=True,null=True)
    data_file = models.CharField(max_length=100)
    data_file_line = models.IntegerField()
    data_file_link = models.URLField(max_length=200)

    class Meta:
        unique_together = ('trip_id','index')


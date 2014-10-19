from django.db import models
from django.conf import settings
import pytz

def get_localtime(dt):
    tz = pytz.timezone(settings.TIME_ZONE)
    if dt.tzinfo:
        return dt.astimezone(tz)
    else:
        return tz.localize(dt)

def print_time(dt):
    return get_localtime(dt).strftime('%H:%M')

PRINTED_NAMES = dict()
PRINTED_NAMES['Modiin'] = 'P Modiin'
PRINTED_NAMES['Ashkelon'] = 'Ashkelon'
PRINTED_NAMES['Kfar Sava'] = 'Kfar Sava'
PRINTED_NAMES['Haifa Bat Gallim'] = 'Bat Gallim'
PRINTED_NAMES['Natanya'] = 'Natanya'
PRINTED_NAMES['Atlit'] = 'Atlit'
PRINTED_NAMES['Akko'] = 'Akko'
PRINTED_NAMES['Sderot'] = 'Sderot'
PRINTED_NAMES['Lehavim - Rahat'] = 'Lehavim'
PRINTED_NAMES['Ashdod Ad Halom'] = 'Ashdod'
PRINTED_NAMES['Be\'er Sheva Center'] = 'BS Center'
PRINTED_NAMES['Hadera West'] = 'Hadera West'
PRINTED_NAMES['Haifa Hof HaKarmel (Razi\'el)'] = 'Hof HaKarmel'
PRINTED_NAMES['Yavne'] = 'Yavne'
PRINTED_NAMES['Kiryat Gat'] = 'Kiryat Gat'
PRINTED_NAMES['Rishon LeTsiyyon - Moshe Dayan'] = 'Moshe Dayan'
PRINTED_NAMES['Bat Yam - Komemiyyut'] = 'Komemiyyut'
PRINTED_NAMES['Kiryat Motzkin'] = 'Kiryat Motzkin'
PRINTED_NAMES['Kesariyya - Pardes Hanna'] = 'Kesariyya'
PRINTED_NAMES['Rehovot E. Hadar'] = 'Rehovot'
PRINTED_NAMES['Petah Tikva Sgulla'] = 'Sgulla'
PRINTED_NAMES['Petah Tikva   Kiryat Arye'] = 'Kiryat Arye'
PRINTED_NAMES['Haifa Center HaShmona'] = 'Haifa Center'
PRINTED_NAMES['Lod'] = 'Lod'
PRINTED_NAMES['Bet Yehoshua'] = 'Bet Yehoshua'
PRINTED_NAMES['Leb Hmifratz'] = 'Leb Hmifratz'
PRINTED_NAMES['Dimona'] = 'Dimona'
PRINTED_NAMES['Be\'er Sheva North University'] = 'BS North'
PRINTED_NAMES['Hod HaSharon'] = 'Hod HaSharon'
PRINTED_NAMES['Ben Gurion Airport'] = 'Natbag'
PRINTED_NAMES['Modiin Center'] = 'Modiin'
PRINTED_NAMES['Bet Shemesh'] = 'Bet Shemesh'
PRINTED_NAMES['Tel Aviv Center - Savidor'] = 'Savidor'
PRINTED_NAMES['Herzliyya'] = 'Herzliyya'
PRINTED_NAMES['Yavne - West'] = 'Yavne - West'
PRINTED_NAMES['Hutsot HaMifrats'] = 'Hutsot HaMifrats'
PRINTED_NAMES['Rishon LeTsiyyon HaRishonim'] = 'HaRishonim'
PRINTED_NAMES['Jerusalem Malha'] = 'Malha'
PRINTED_NAMES['Rosh Ha\'Ayin North'] = 'Rosh Ha\'Ayin'
PRINTED_NAMES['Bat Yam - Yoseftal'] = 'Yoseftal'
PRINTED_NAMES['Ganey Aviv'] = 'Ganey Aviv'
PRINTED_NAMES['Kfar Habbad'] = 'Kfar Habbad'
PRINTED_NAMES['Tel Aviv - University'] = 'TA University'
PRINTED_NAMES['Tel Aviv HaHagana'] = 'HaHagana'
PRINTED_NAMES['Kiryat Hayyim'] = 'Kiryat Hayyim'
PRINTED_NAMES['Nahariyya'] = 'Nahariyya'
PRINTED_NAMES['Ramla'] = 'Ramla'
PRINTED_NAMES['Tel Aviv HaShalom'] = 'TA HaShalom'
PRINTED_NAMES['Holon Junction'] = 'Holon Junction'
PRINTED_NAMES['Bne Brak'] = 'Bne Brak'
PRINTED_NAMES['Be\'er Ya\'akov'] = 'Be\'er Ya\'akov'
PRINTED_NAMES['Binyamina'] = 'Binyamina'
PRINTED_NAMES['Jerusalem Biblical Zoo'] = 'Biblical Zoo'
PRINTED_NAMES['Holon - Wolfson'] = 'Wolfson'

for k,v in PRINTED_NAMES.iteritems():
    assert len(v) <= 17,'%s => %s too long' % (k,v)


def print_stop_name(stop_name):
    return PRINTED_NAMES.get(stop_name,stop_name)

class Sample(models.Model):
    date = models.DateField(db_index=True)
    train_num = models.IntegerField(db_index=True)
    arrive_expected = models.DateTimeField()
    arrive_actual = models.DateTimeField()
    arrive_delay = models.FloatField()
    depart_expected = models.DateTimeField()
    depart_actual = models.DateTimeField()
    depart_delay = models.FloatField()
    stop_id = models.IntegerField(db_index=True)
    stop_name = models.CharField(max_length=40)
    csv_line = models.IntegerField(unique=True)
    time_in_station = models.FloatField()


    #class Meta:
    #    unique_together = ('csv_line'date','train_num','arrive_expected','depart_expected')
    def __unicode__(self):
        return '{stop_id:4d} {stop_name:17s}: A={aa}({ae}) D={da}({de})'.format(aa=print_time(self.arrive_actual),
                                                                     ae=print_time(self.arrive_expected),
                                                                     da=print_time(self.depart_actual),
                                                                     de=print_time(self.depart_expected),
                                                                     stop_id=self.stop_id,
                                                                     stop_name=print_stop_name(self.stop_name))

class Trip(models.Model):
    date = models.DateField(db_index=True)
    train_num = models.IntegerField(db_index=True)
    stops_count = models.IntegerField()
    final_delay = models.FloatField()
    max_arrive_delay = models.FloatField()
    max_depart_delay = models.FloatField()

    def __unicode__(self):
        return 'Trip %s in %s' % (self.train_num,self.date)

    def get_samples(self):
        return list(Sample.objects.filter(date=self.date,train_num=self.train_num).order_by('arrive_expected'))


from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import logging
import data.stop_utils
from django.utils.translation import activate
from data.models import Sample
from data.models import Stop
from django.db.models import Avg

# Run this file using: python manage.py passenger_based_benchmarks


LOGGER = logging.getLogger(__name__)
# Stats are from 2015 from this source:
# http://www.tapuz.co.il/forums/viewmsg/394/182147123

average_arriving_passengers = {}
average_arriving_passengers["Modiin"] = 15250;
average_arriving_passengers["Modiin Center"] = 67051;
average_arriving_passengers["Kiryat Hayyim"] = 14964;
average_arriving_passengers["Kiryat Motzkin"] = 80116;
average_arriving_passengers["Leb Hmifratz"] = 95312;
average_arriving_passengers["Hutsot HaMifrats"] = 16995;
average_arriving_passengers["Akko"] = 96326;
average_arriving_passengers["Nahariyya"] = 109325;
average_arriving_passengers["Haifa Center HaShmona"] = 68441;
average_arriving_passengers["Haifa Bat Gallim"] = 70922;
average_arriving_passengers["Haifa Hof HaKarmel (Razi'el)"] = 182713;
average_arriving_passengers["Atlit"] = 10667;
average_arriving_passengers["Binyamina"] = 105365;
average_arriving_passengers["Kesariyya - Pardes Hanna"] = 39595;
average_arriving_passengers["Hadera West"] = 81147;
average_arriving_passengers["Natanya"] = 220717;
average_arriving_passengers["Bet Yehoshua"] = 92672;
average_arriving_passengers["Herzliyya"] = 110025;
average_arriving_passengers["Tel Aviv - University"] = 204597;
average_arriving_passengers["Tel Aviv Center - Savidor"] = 688883;
average_arriving_passengers["Bne Brak"] = 50594;
average_arriving_passengers["Petah Tikva   Kiryat Arye"] = 58094;
average_arriving_passengers["Petah Tikva Sgulla"] = 31535;
average_arriving_passengers["Tel Aviv HaShalom"] = 609636;
average_arriving_passengers["Holon Junction"] = 22142;
average_arriving_passengers["Holon - Wolfson"] = 24698;
average_arriving_passengers["Bat Yam - Yoseftal"] = 63970;
average_arriving_passengers["Bat Yam - Komemiyyut"] = 30782;
average_arriving_passengers["Kfar Habbad"] = 12427;
average_arriving_passengers["Tel Aviv HaHagana"] = 225254;
average_arriving_passengers["Lod"] = 97794;
average_arriving_passengers["Ramla"] = 30413;
average_arriving_passengers["Ganey Aviv"] = 19240;
average_arriving_passengers["Rehovot E. Hadar"] = 206661;
average_arriving_passengers["Be'er Ya'akov"] = 16441;
average_arriving_passengers["Yavne"] = 20496;
average_arriving_passengers["Ashdod Ad Halom"] = 134841;
average_arriving_passengers["Ashkelon"] = 93906;
average_arriving_passengers["Bet Shemesh"] = 34665;
average_arriving_passengers["Jerusalem Biblical Zoo"] = 554;
average_arriving_passengers["Jerusalem Malha"] = 17667;
average_arriving_passengers["Kiryat Gat"] = 33332;
average_arriving_passengers["Be'er Sheva North University"] = 70171;
average_arriving_passengers["Be'er Sheva Center"] = 115593;
average_arriving_passengers["Dimona"] = 620;
average_arriving_passengers["Lehavim - Rahat"] = 15057;
average_arriving_passengers["Ben Gurion Airport"] = 138261;
average_arriving_passengers["Kfar Sava"] = 55295;
average_arriving_passengers["Rosh Ha'Ayin North"] = 54556;
average_arriving_passengers["Yavne - West"] = 49248;
average_arriving_passengers["Rishon LeTsiyyon HaRishonim"] = 26490;
average_arriving_passengers["Hod HaSharon"] = 40790;
average_arriving_passengers["Sderot"] = 33278;
average_arriving_passengers["Rishon LeTsiyyon - Moshe Dayan"] = 79377;
average_arriving_passengers["Netivot"] = 28555;
average_arriving_passengers["Ofakim"] = 26761;
average_arriving_passengers["Migdal Haeemek Kfar Baruch"] = 9007;
average_arriving_passengers["Yoknema - Kfar Yehosua"] = 12766;
average_arriving_passengers["Netanya Sapir"] = 8468;
average_arriving_passengers["Beit Shean"] = 21192;
average_arriving_passengers["Afula"] = 28727;
average_arriving_passengers["Achihud"] = 0;
average_arriving_passengers["Motzkin"] = 0;

class Command(BaseCommand):
    def handle(self, *args, **options):
        #LOGGER.info("Average delay: %.2f ", Sample.objects.aggregate(c=Avg("delay_arrival"))["c"]);
        #samples_ontime = Sample.objects.filter(delay_arrival__lt=5*60).count()
        #samples_delayed = Sample.objects.filter(delay_arrival__gte=5*60).count()
        #all_samples = samples_ontime + samples_delayed
        total_passengers = sum(average_arriving_passengers.values())
        ontime_weighted_average = 0
        for stop in Stop.objects.all():
            samples_ontime = Sample.objects.filter(stop__gtfs_stop_id=stop.gtfs_stop_id).filter(delay_arrival__lt=5*60).count()
            samples_delayed = Sample.objects.filter(stop__gtfs_stop_id=stop.gtfs_stop_id).filter(delay_arrival__gte=5*60).count()
            ontime_weighted_average += samples_ontime / (samples_ontime + samples_delayed) * average_arriving_passengers[stop.english]/total_passengers
            print("%s\t%.2f" % (stop.english, samples_ontime / (samples_ontime + samples_delayed)))
            #print(average_arriving_passengers[stop.english]/total_passengers)

        LOGGER.info("Weighted ontime (less than 5 minutes delay): %.2f ", ontime_weighted_average)
        #LOGGER.info("Ontime (less than 5 minutes delay): %.2f ", samples_ontime/all_samples)
        
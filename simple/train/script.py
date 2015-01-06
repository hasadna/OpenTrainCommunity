from data.models import Trip
def main():
    limit = 100
    offset = 0
    count = 0
    total_trips = Trip.objects.count()
    while True:
        trips = Trip.objects.order_by('id')[offset:offset+limit]
        trips = list(trips)
        count += len(trips)
        if not trips:
            break
        for trip in trips:
            trip.sample_set.all().update(stop_ids=trip.stop_ids)
            print 'Trips %s/%s done' % (count,total_trips)
        
        offset+=limit

    print 'count = %s' % count



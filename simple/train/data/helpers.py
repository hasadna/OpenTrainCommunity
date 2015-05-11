from models import Sample

def samples_with_0_delay(stop_id):
    samples = Sample.objects.filter(valid=True,
                                    stop_id=stop_id,
                                    actual_departure__isnull=False,
                                    actual_arrival__isnull=False,
                                    exp_departure__isnull=False,
                                    exp_arrival__isnull=False)
    result =[s for s in samples if not s.actual_departure - s.actual_arrival and not s.exp_departure - s.exp_arrival]
    return result

def trips_with_0_delay(stop_id):
    samples = samples_with_0_delay(stop_id)
    return set(s.trip_id for s in samples)



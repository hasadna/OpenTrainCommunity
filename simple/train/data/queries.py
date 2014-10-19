from models import Trip,Sample

def get_mid_delay_trips():
    trips = Trip.objects.raw('''select * from data_trip
    where max_arrive_delay - final_delay > 15
    and max_arrive_delay - final_delay < 30
    and final_delay < 5 and max_arrive_delay > 0''')
    return list(trips)






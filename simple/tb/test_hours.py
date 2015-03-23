import requests
import collections

url = 'http://localhost:8000/api/path-info-full?stop_ids=400,300,8600,4900,4600,3700'

class Table(object):
    def __init__(self, data):
        self.data = data

    def get_week_day_hours(self, week_day):
        result = []
        for d in self.data:
            if d['info']['week_day'] == week_day and d['info']['hours'] != 'all':
                result.append(d)
        assert len(result) == 8
        return result
    
    def get_week_day_all(self, week_day):
        result = []
        for d in self.data:
            if d['info']['week_day'] == week_day and d['info']['hours'] == 'all':
                result.append(d)
        assert len(result) == 1
        return result[0]

    def check_week_day(self, wd):
        hours = self.get_week_day_hours(wd)
        all = self.get_week_day_all(wd)
        trips_by_hours = sum(h['info']['num_trips'] for h in hours)
        assert all['info']['num_trips'] == trips_by_hours,'%s <-> %s' % (all['info']['num_trips'],trips_by_hours)

def main():
    r = requests.get(url)
    data = r.json()
    t = Table(data)
    for wd in [1,2,3,4,5,6,7]:
        t.check_week_day(wd)
    
        
        
if __name__ == '__main__':
    main()

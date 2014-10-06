import codecs
import re
import datetime
import argparse

LINE_RE = re.compile(r'^\s*' +
                     r'(?P<date>\d+)\s+"' +
                     r'(?P<train_num>\d+)"\s+' +
                     r'(?P<exp_arrival>\d+)\s+' +
                     r'(?P<actual_arrival>\d+)\s+' +
                     r'(?P<exp_departure>\d+)\s+' +
                     r'(?P<actual_departure>\d+)\s+' +
                     r'(?P<raw_stop_id>\d+)\s+' +
                     r'"(?P<raw_stop_name>.*)"\s*$')
    
class TrainTrip():
    def __init__(self,date,train_num):
        self.date = date
        self.train_num = train_num
        self.times = list(TrainData.objects.filter(date=date,train_num=train_num).order_by('exp_arrival'))
        if not self.times:
            raise Exception('no trip num %s on %s' % (train_num,date))
    def print_nice(self):
        print '--------------------------------------------------'
        print '%s @%s' % (self.train_num,self.date)
        late = self.get_avg_late()
        max_late = self.get_max_late()
        last_late = self.get_last_late()
        print 'Avg Late : %d mins %d secs' % (late / 60,late % 60)
        print 'Max Late : %d mins %d secs' % (max_late / 60,max_late % 60)
        print 'Last Late: %d mins %d secs' % (last_late / 60,last_late % 60)
        print '--------------------------------------------------'
        for t in self.times:
            print '%(line)5d %(stop_name)-30s %(actual_arrival)4s (%(exp_arrival)4s)  %(actual_departure)4s (%(exp_departure)4s)' % ( 
                                                            {'line' : t.line,
                                                           'stop_name' : t.stop.stop_name,
                                                            'actual_arrival' : t.actual_arrival,
                                                             'actual_departure' : t.actual_departure,
                                                            'exp_arrival' : t.exp_arrival,
                                                            'exp_departure' : t.exp_departure})
    def get_lates(self):
        return [line.get_arrival_late() for line in self.times[1:]]
        
    def get_avg_late(self):
        lates = self.get_lates()
        return sum(lates)/len(lates)
    
    def get_last_late(self):
        lates = self.get_lates()
        return lates[-1]
    
    def get_max_late(self):
        lates = self.get_lates()
        return max(lates)                      

                     
def _parse_date(date):
    year = int(date[0:4])
    month = int(date[4:6])
    day = int(date[6:8])
    return datetime.date(year=year,month=month,day=day)
                     
def get_stop_ids():
    import gtfs.models
    stop_ids = set(gtfs.models.Stop.objects.all().values_list('stop_id',flat=True))
    return stop_ids
                     
def read_file(fname):
    stop_ids = get_stop_ids()
    with codecs.open(fname,encoding="windows-1255") as fh:
        tds = []
        for idx,line in enumerate(fh):
            m = LINE_RE.match(line)
            if m:
                td = TrainData()
                gd = m.groupdict()
                td.date = _parse_date(gd['date'])
                td.train_num = gd['train_num']
                td.exp_arrival = gd['exp_arrival']
                td.actual_arrival = gd['actual_arrival']
                td.exp_departure = gd['exp_departure']
                td.actual_departure = gd['actual_departure']
                td.raw_stop_id = int(gd['raw_stop_id'])
                td.raw_stop_name = gd['raw_stop_name']
                td.file = fname
                td.line = idx
                if td.raw_stop_id in stop_ids:
                    td.stop_id = td.raw_stop_id
                    tds.append(td)
            else:
                raise Exception('Illegal line %d at %s' % (idx,fname))
    print 'Created %d entries. Saving to db' % (len(tds))
    TrainData.objects.bulk_create(tds)
    print 'Saved'
    
def read_year_month(year,month):
    """ read file of month/year """
    read_file('traindata/data/%02d_%s.txt' % (month,year))
    
def get_trains_for_day(d):
    """ return all train nums for specific day """
    trains = TrainData.objects.filter(date=d).values_list('train_num',flat=True).distinct()
    return trains

def get_trains_for_day_stop(d,stop):
    """ return all train nums for specific day """
    trains = TrainData.objects.filter(date=d,stop=stop).values_list('train_num',flat=True).distinct()
    return trains

class TrainParser():
    def __init__(self,input,output,append):
        self.ifile = input
        self.append = append
        self.ofile = output

    def parse(self):
        with codecs.open(self.ifile,encoding="windows-1255") as ifh:
            for idx,line in enumerate(ifh):
                self.parse_line(idx,line)

    def parse_line(self,idx,line):
        pass

def main():
    parser = argparse.ArgumentParser('parser')
    parser.add_argument('--input',required=True)
    parser.add_argument('--output',required=False)
    parser.add_argument('--append',required=False,default=True,action='store_true')
    ns = parser.parse_args()
    tp = TrainParser(**vars(ns))
    tp.parse()

if __name__ == '__main__':
    main()

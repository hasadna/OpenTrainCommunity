from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import entities
from entities import Station, TrainStop
import datetime
import time
import os

Base = declarative_base()
ENGINE_STRING = 'postgresql://admin:admin@localhost/opentrain_community'
real_stops = [300, 400, 700, 800, 1220, 1300, 1500, 1600, 2100, 2200, 2300, 2500, 2800, 2820, 3100, 3300, 3400, 3500, 3600, 3700, 4100, 4170, 4250, 4600, 4640, 4660, 4680, 4690, 4800, 4900, 5000, 5010, 5150, 5200, 5300, 5410, 5800, 5900, 6300, 6500, 6700, 7000, 7300, 7320, 7500, 8550, 8600, 8700, 8800, 9000, 9100, 9200, 9600, 9800]  

def get_session():
  engine = create_engine(ENGINE_STRING)
  # Bind the engine to the metadata of the Base class so that the
  # declaratives can be accessed through a DBSession instance
  Base.metadata.bind = engine

  DBSession = sessionmaker(bind=engine)
  session = DBSession()
  return session

def create_db():
  drop_db()
  entities.create_db()

def drop_db():
  from sqlalchemy.engine import reflection
  from sqlalchemy import create_engine
  from sqlalchemy.schema import (
      MetaData,
      Table,
      DropTable,
      ForeignKeyConstraint,
      DropConstraint,
      )
  
  engine = create_engine(ENGINE_STRING)
  
  conn = engine.connect()
  
  # the transaction only applies if the DB supports
  # transactional DDL, i.e. Postgresql, MS SQL Server
  trans = conn.begin()
  
  inspector = reflection.Inspector.from_engine(engine)
  
  # gather all data first before dropping anything.
  # some DBs lock after things have been dropped in 
  # a transaction.
  
  metadata = MetaData()
  
  tbs = []
  all_fks = []
  
  for table_name in inspector.get_table_names():
      fks = []
      for fk in inspector.get_foreign_keys(table_name):
          if not fk['name']:
              continue
          fks.append(
              ForeignKeyConstraint((),(),name=fk['name'])
              )
      t = Table(table_name,metadata,*fks)
      tbs.append(t)
      all_fks.extend(fks)
  
  for fkc in all_fks:
      conn.execute(DropConstraint(fkc))
  
  for table in tbs:
      conn.execute(DropTable(table))
  
  trans.commit()

def _parse_timedelta(timestr):
  while len(timestr) < 4:
    timestr = '0' + timestr  
  minutes = int(timestr[0:2])*60 + int(timestr[2:4])  
  return datetime.timedelta(minutes=minutes)

def _parsedate(datestr):
  datestr = datestr.strip()
  date_val = datetime.datetime.strptime(datestr, '%Y%m%d')
  return date_val

def add_opentrain_data(filename):
  session = get_session()
  with open(filename, 'r') as f:
    lines = f.readlines()
  max_lines = 200000000
  count = 0
  row_count = min(len(lines), max_lines)
  for line in lines:
    count += 1
    if count > max_lines:
      break
    if count % 10000 == 0:
      print 'Done {}%'.format(int(count/float(row_count)*100))
      session.commit()
    line_data = line.split('\t')
    date = _parsedate(line_data[0])
    train_num = int(line_data[1].strip("\""))
    arrive_expected = date + _parse_timedelta(line_data[2])
    arrive_actual = date + _parse_timedelta(line_data[3])
    depart_expected = date + _parse_timedelta(line_data[4])
    depart_actual = date + _parse_timedelta(line_data[5])
    station_id = int(line_data[6])
    if station_id not in real_stops:
      continue
    train_stop = TrainStop(date=date, 
                           train_num=train_num, 
                           arrive_expected=arrive_expected, 
                           arrive_actual=arrive_actual,
                           depart_expected=depart_expected, 
                           depart_actual=depart_actual,
                           station_id=station_id)
    session.add(train_stop)
  session.commit()
  print 'Done all'

if __name__ == "__main__":
  session = get_session()
  #create_db()
  #add_opentrain_data(os.path.abspath('../data/01_2013.txt'))
  query = session.query(TrainStop).filter(TrainStop.date == datetime.date(2013, 1, 1))
  trainstops = query.all()
  for x in trainstops:
    arrive_delay = (x.arrive_actual - x.arrive_expected).total_seconds()/60
    depart_delay = (x.depart_actual - x.depart_expected).total_seconds()/60
    print "{},{},{},{},{},{},{},{},{}".format(x.date, x.train_num, 
                                              x.arrive_expected,#.strftime('%H:%M'), 
                                              x.arrive_actual,#.strftime('%H:%M'), 
                                              arrive_delay, 
                                              x.depart_expected,#.strftime('%H:%M'), 
                                              x.depart_actual,#.strftime('%H:%M'), 
                                              depart_delay, x.station_id)

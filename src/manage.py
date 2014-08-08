from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import entities

Base = declarative_base()
ENGINE_STRING = 'postgresql://admin:admin@localhost/opentrain_community'

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
    
def add_opentrain_data(filename):
  from sqlalchemy import create_engine
  from sqlalchemy.orm import sessionmaker
   
  from entities import Station, TrainStop
   
  engine = create_engine(ENGINE_STRING)
  # Bind the engine to the metadata of the Base class so that the
  # declaratives can be accessed through a DBSession instance
  Base.metadata.bind = engine
   
  DBSession = sessionmaker(bind=engine)
  # A DBSession() instance establishes all conversations with the database
  # and represents a "staging zone" for all the objects loaded into the
  # database session object. Any change made against the objects in the
  # session won't be persisted into the database until you call
  # session.commit(). If you're not happy about the changes, you can
  # revert all of them back to the last commit by calling
  # session.rollback()
  session = DBSession()
   
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
      session = DBSession()
    line_data = line.split('\t')
    date = int(line_data[0])
    train_num = int(line_data[1].strip("\""))
    # WATCH OUT!!! - the order here is all made up:
    arrive_expected = int(line_data[2])
    arrive_actual = int(line_data[3])
    depart_expected = int(line_data[4])
    depart_actual = int(line_data[5])
    station_id = int(line_data[6])
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
  create_db()
  add_opentrain_data()


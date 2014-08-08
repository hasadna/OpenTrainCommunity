import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

 
Base = declarative_base()
 
class Station(Base):
  __tablename__ = 'station'
  id = Column(Integer, primary_key=True)
  english_name = Column(String(250), nullable=False)
  is_real_station = Column(Boolean, nullable=False)

 
class TrainStop(Base):
  __tablename__ = 'trainstop'
  id = Column(Integer, primary_key=True)
  date = Column(Date, nullable=False)
  train_num = Column(Integer, nullable=False)
  depart_expected = Column(DateTime)
  depart_actual = Column(DateTime)
  arrive_expected = Column(DateTime)
  arrive_actual = Column(DateTime)
  
  station_id = Column(Integer)
  #station_id = Column(Integer, ForeignKey('station.id'))
  #station = relationship(Station)
 
def create_db():
  from sqlalchemy import create_engine
  ENGINE_STRING = 'postgresql://admin:admin@localhost/opentrain_community'
  engine = create_engine(ENGINE_STRING)
  Base.metadata.create_all(engine)

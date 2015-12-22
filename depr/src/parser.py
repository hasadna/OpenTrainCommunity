#! /usr/bin/env python
"""Parser and analyser for Israel Railways data
Example usage:
parser.py -f ../data/stops_ids_and_names.txt -i ../data/01_2013.txt --../output-station-stats output.csv
"""


import sys
import os
import ministorm
import bolts
import argparse
from entities import TrainStop
import manage
import datetime

class MyTopology(ministorm.Topology):

  def __init__(self, args):
    ministorm.Topology.__init__(self)
    self._args = args

  def create(self):
    # creating the bolts
    session = manage.get_session()
    query = session.query(TrainStop)#.filter(TrainStop.date == datetime.date(2013, 1, 1))
    trainstops = query.all()
    #spout = self.addbolt(bolts.FileSpout('rawlines', self._args.input_db_file[0]))
    spout = self.addbolt(bolts.SQLAlchemyToLineSpout('rawlines', trainstops))
    spoutnames = self.addbolt(bolts.FileSpout('rawnames', self._args.station_names_file[0]))
    lineparser = self.addbolt(bolts.LineParserBolt())
    noname = self.addbolt(bolts.StationNonameFilter())
    rushhours = self.addbolt(bolts.TimeFilter([ ('07:00', '10:00'), ('17:00', '19:00') ]))
    delaycalc = self.addbolt(bolts.DelayCalculatorBolt())
    stationsstats = self.addbolt(bolts.StationsStatsBolt())
    stationsprinting = self.addbolt(bolts.CSVPrintingSink('stationsstats', self._args.output_station_stats[0]))
  
    #trainstats = self.addbolt(bolts.TrainStationStatsBolt())
    #trainavgdelay = self.addbolt(bolts.TrainStationAvgDelayBolt())
  
    # connecting them
    ministorm.Stream('rawlines', spout, lineparser)
    ministorm.Stream('rawnames', spoutnames, lineparser)
    ministorm.Stream('parsedlines', lineparser, noname)
    ministorm.Stream('parsedlines', noname, rushhours)
    ministorm.Stream('parsedlines', rushhours, delaycalc)
    ministorm.Stream('parsedlines_delay', delaycalc, stationsstats)
    ministorm.Stream('stationsstats', stationsstats, stationsprinting)

    #ministorm.Stream('parsedlines_delay', delaycalc, trainstats)
    #ministorm.Stream('rawnames', spoutnames, trainavgdelay)
    #ministorm.Stream('trainstationstats', trainstats, trainavgdelay)
    #ministorm.Stream('trainstationavgdelay', trainavgdelay, trainsprinting)



if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Opentrain parser test - station average delay')
  parser.add_argument('-f', '--station-names-file', \
    required=True,\
    type=argparse.FileType('r'),\
    nargs=1,\
    help='The station names file, containing tuples of (station id, station name)')
  parser.add_argument('-i', '--input-db-file', \
    required=False,\
    type=argparse.FileType('r'),\
    nargs=1,\
    help='The database file')
  parser.add_argument('--output-station-stats',
    type=argparse.FileType('w'),\
    required=True,\
    nargs=1,\
    help='Station stats output file name')

  args = parser.parse_args()

  try:
    topology = MyTopology(args)
    topology.create()
    topology.calc()
  except Exception as e:
    print str(e)
  print 'Parser done'


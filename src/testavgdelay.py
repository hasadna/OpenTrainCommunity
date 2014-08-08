#! /usr/bin/env python

import ministorm
from bolts import Bolt
import bolts
import sys
import random
import argparse

class AvgStationDelayTestSpout(Bolt):
	"""
	Create a test according to a given average delay
	Input streams: none
	Output streams: rawlines
	"""
	def _mins2str(self, t):
		return '%02d%02d' % ( (t/60), (t%60) )

	def _genline(self, stationum, planned_arrival, defacto_arrival):
		"""
		Columns:
			date
			train_num
			planned_arrival
			defacto_arrival
			planned_departure
			defacto_departure
			station_num
			station_name
		"""
		return '20130101\t"%d"\t%s\t%s\t%d\t%d\t%d\t" no name"' % (\
			random.randint(10, 900),\
			self._mins2str(planned_arrival),\
			self._mins2str(defacto_arrival),\
			0,\
			1,\
			stationum)

	def __init__(self, delayfromstationum, sz):
		Bolt.__init__(self)
		self._delayfromstationum = delayfromstationum
		self._sz = sz

	def check(self):
		self.checkoutputstreams(['rawlines'])

	def run(self):
		for i in xrange(self._sz):
			stationum = random.sample(self._delayfromstationum.keys(), 1)[0]
			avg_delay = self._delayfromstationum[stationum]
			delay = int(0.5 + random.expovariate(1.0 / avg_delay))
			s = random.randint(0, 60 * 24 - delay)
			line = self._genline(stationum, s, s+delay)
			#print line
			self.write('rawlines', line)

		self.doneall()

class AvgStationDelayTestSink(Bolt):
	"""
	Check average delay is as expected
	Input streams: 1 stationsstats
	Output streams: none
	"""
	
	def __init__(self, delayfromstationum, slack):
		Bolt.__init__(self)
		self._delayfromstationum = delayfromstationum
		self._slack = slack
	
	def check(self):
		self.checkinputstreams({'stationsstats': 1})

	def __str__(self):
		return 'AvgStationDelayTestSink'

	def _validate(self):
		if sorted(self._results.keys()) != sorted(self._delayfromstationum.keys()):
			print 'FAILED keys missmatch'
			return
		
		diffs = map(lambda k: (self._results[k], self._delayfromstationum[k]), self._results.keys())
		bigdiffs = filter(lambda (res,expected): abs(res-expected) > self._slack, diffs)
	
		for (res, expected) in bigdiffs:
			print 'FAILED, delay mismatch: expected %.3f got %.3f' % (expected, res)
		
		if len(bigdiffs) == 0:
			print 'SUCCESS, max difference was %.3f' % \
				max(map(lambda (res, expected): abs(res-expected), diffs))


	def run(self):
		self._results = {}
		print 'Testing %s ... ' % str(self)
		while True:
			l = self.read('stationsstats')
			if l == None:
				break
			self._results[l['station_num']] = l['avg_delay']
		self.doneall()
		self._validate()


class AvgStationDelayTestTopology(ministorm.Topology):


	def __init__(self, nrlines, diffslack, stationames):
		ministorm.Topology.__init__(self)
		self._stationames = stationames
		self._nrlines = nrlines		# number of records in test
		self._diffslack = diffslack 	# slack allowed by the random generator	
		# data for the test: station number -> average delay
		self._avgdelay = {\
			6300: 1.0,\
			6500: 2.5,\
			7000: 5.1,\
		}

	def create(self):
		# create test spout
		spout = self.addbolt(AvgStationDelayTestSpout(self._avgdelay, self._nrlines))

		# creating the bolts
		spoutnames = self.addbolt(bolts.FileSpout('rawnames', self._stationames))
		lineparser = self.addbolt(bolts.LineParserBolt())
		noname = self.addbolt(bolts.StationNonameFilter())
		delaycalc = self.addbolt(bolts.DelayCalculatorBolt())
		stationsstats = self.addbolt(bolts.StationsStatsBolt())
		
		# create test bolts
		avgstationdelay = self.addbolt(AvgStationDelayTestSink(self._avgdelay, self._diffslack))

		# connecting them
		ministorm.Stream('rawlines', spout, lineparser)
		ministorm.Stream('rawnames', spoutnames, lineparser)
		ministorm.Stream('parsedlines', lineparser, noname)
		ministorm.Stream('parsedlines', noname, delaycalc)
		ministorm.Stream('parsedlines_delay', delaycalc, stationsstats)
		ministorm.Stream('stationsstats', stationsstats, avgstationdelay)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Opentrain parser test - station average delay')
	parser.add_argument('-f', '--station-names-file', \
		required=True,\
		type=argparse.FileType('r'),\
		nargs=1,\
		help='The station names file, containing tuples of (station id, station name)')

	parser.add_argument('-n', '--nr-records', \
		type=int,\
		nargs=1,\
		default=100000,\
		help='Number of records to run in test')

	parser.add_argument('-s', '--test-slack', \
		type=float,\
		nargs=1,\
		default=0.1,\
		help='Allowed error margin for test')

	args = parser.parse_args()
	try:
		topology = AvgStationDelayTestTopology(args.nr_records, args.test_slack, args.station_names_file[0])
		topology.create()
		topology.calc()
	except Exception as e:
		print str(e)


#! /usr/bin/env python

from ministorm import Bolt

class FileSpout(Bolt):
	
	"""
	Read raw data provided by Israeli railways
	Input streams: None
	Output streams: a raw line
	"""

	def __init__(self, outputlabel, fileobj):
		Bolt.__init__(self)
		self._outputlabel = outputlabel
		self._f = fileobj

	def check(self):
		self.checkinputstreams({})
		self.checkoutputstreams([self._outputlabel])
		
	def run(self):
		for line in self._f:
			self.write(self._outputlabel, line)
		self.doneall()


class PrintingSink(Bolt):
	
	"""
	Print all the inputs it is given
	Input streams: any type of stream
	Output streams: None
	"""

	def __init__(self, inputs):
		Bolt.__init__(self)
		self._inputs = inputs

	def _printinputs(self, label):
		r = range(self._inputs[label])
		r = map(lambda i: self.read(label, i), r)
		r = filter(lambda x: x != None, r)
		if len(r) == 0:
			return False
		for x in r:
			print str(x)
		return True

	def check(self):	
		self.checkinputstreams(self._inputs)

	def run(self):
		while True:
			printed = map(lambda label: self._printinputs(label), self._inputs.keys())
			# check if we printed anything
			if True not in printed:
				break
		self.doneall()


class CSVPrintingSink(Bolt):
	
	"""
	Print input in a CSV format
	Input streams: any type of stream
	Output streams: None
	"""

	def __init__(self, inputuple, outputfile):
		Bolt.__init__(self)
		self._inputuple = inputuple
		self._printedheader = False
		self._outputfile = outputfile

	def check(self):
		self.checkinputstreams({self._inputuple: 1})

	def run(self):
		while True:
			l = self.read(self._inputuple)
			if l == None:
				break
			keys = sorted(l.keys())
			if not self._printedheader:
				self._printedheader = True
				self._outputfile.write(','.join(keys))
				self._outputfile.write('\n')
			vals = map(lambda k: str(l[k]), keys)
			self._outputfile.write(','.join(vals))
			self._outputfile.write('\n')
		self.doneall()


class LineParserBolt(Bolt):

	"""
	Parse the raw lines into dictonaries
	Input streams: 1 rawline stream, 1 rawnames stream
	Output streams: parsedlines stream
	"""

	def _parsetime(self, timestr):
		while len(timestr) < 4:
			timestr = '0'+timestr
		timestr = timestr[0:2] + ':'+timestr[2:4]
		return timestr
	
	def _parseline(self, line):
		params = line.strip().split()
		
		date = params[0]
		date = date[0:4] + '-' + date[4:6] + '-' + date[6:8]
		
		stationum = int(params[6])
		stationame = None
		if stationum in  self._namefromnum.keys():
			stationame = self._namefromnum[stationum]

		return {\
			'date': date,\
			'train_num': int(params[1].strip('"')),\
			'planned_arrival': self._parsetime(params[2]),\
			'defacto_arrival': self._parsetime(params[3]),\
			'planned_departure': self._parsetime(params[4]),\
			'defacto_departure': self._parsetime(params[5]),\
			'station_num': stationum,\
			'station_name': stationame,\
			}
	def check(self):
		self.checkinputstreams({'rawlines':1, 'rawnames': 1})
		self.checkoutputstreams(['parsedlines'])
		
	def run(self):
		self._namefromnum = {}
		while True:
			line = self.read('rawnames')
			if line == None:
				break
			station_num = int(line.split()[0])
			station_name = ' '.join(line.split()[1:])
			self._namefromnum[station_num] = station_name

		while True:
			line = self.read('rawlines')
			if line == None:
				break
			parsed = self._parseline(line)
			self.write('parsedlines', parsed)
		self.doneall()
		

class BlackholeSink(Bolt):

	"""
	Read input streams and does nothing with them
	Input streams: any type of input stream
	Output streams: None
	"""

	def __init__(self, inputs):
		Bolt.__init__(self)
		self._inputs = inputs

	def check(self):
		pass

	def run(self):
		while True:
			r = map(lambda label: self.read(label), self._inputs)
			r = filter(lambda x: x != None, r)
			if len(r) == 0:
				break
		self.doneall()


class LineStationsBolt(Bolt):

	"""
	Create a map from train number to the station it passes
	Input streams: 1 parsedlines
	Output streams: stationsfromline
	"""
	
	def __init__(self):
		Bolt.__init__(self)
		self._stationsfromline = {}

	def _addstation(self, trainum, station):
		if trainum not in self._stationsfromline.keys():
			self._stationsfromline[trainum] = set()
		self._stationsfromline[trainum].add(station)
	
	def check(self):		
		self.checkinputstreams({'parsedlines':1})
		self.checkoutputstreams(['stationsfromline'])

	def run(self):
		while True:
			line = self.read('parsedlines')
			if line == None:
				break
			self._addstation(line['train_num'], line['station_num'])
		self.write('stationsfromline', self._stationsfromline)
		self.doneall()


class TimeFilter(Bolt):

	"""
	Filter lines according to planned arrival. Use this to create a rush hours filter
	Input streams: 1 parsedlines
	Output streams: parsedlines
	"""

	def __init__(self, timeframes):
		Bolt.__init__(self)
		self._timeframes = []
		for (start, end) in timeframes:
			self._timeframes.append((self._tominutes(start), self._tominutes(end)))

	def _tominutes(self, timestr):
		return reduce(lambda x, s: int(x)*60+int(s), timestr.split(':'))

	def _shouldoutput(self, plannedarrival):
		m = self._tominutes(plannedarrival)
		for s,e in self._timeframes:
			if s <= m and m <= e:
				return True
		return False

	def check(self):
		self.checkinputstreams({'parsedlines':1})
		self.checkoutputstreams(['parsedlines'])

	def run(self):
		while True:
			parsedline = self.read('parsedlines')
			if parsedline == None:
				break
			if self._shouldoutput(parsedline['planned_arrival']):
				self.write('parsedlines', parsedline)
		self.doneall()


class StationNonameFilter(Bolt):
	
	"""
	Filter out station without a name
	Input streams: 1 parsedlines
	Output streams: parsedlines
	"""

	def check(self):
		self.checkinputstreams({'parsedlines':1})
		self.checkoutputstreams(['parsedlines'])
	
	def run(self):
		while True:
			parsedline = self.read('parsedlines')
			if parsedline == None:
				break
			if parsedline['station_name'] != None:
				self.write('parsedlines', parsedline)
		self.doneall()
class StationFilter(Bolt):
	
	"""
	Filter lines according to stations
	Input streams: 1 parsedlines
	Output streams: parsedlines
	"""

	def __init__(self, stations):
		Bolt.__init__(self)
		self._stations = stations
	
	def check(self):
		self.checkinputstreams({'parsedlines':1})
		self.checkoutputstreams(['parsedlines'])
	
	def _shouldoutput(self, stationum):
		return stationum in self._stations

	def run(self):
		while True:
			parsedline = self.read('parsedlines')
			if parsedline == None:
				break
			if self._shouldoutput(parsedline['station_num']):
				self.write('parsedlines', parsedline)
		self.doneall()


class DelayCalculatorBolt(Bolt):
	
	"""
	Calculates the delay in minutes
	Input streams: parsedlines
	Output streams: parsedlines_delay
	"""

	def check(self):
		self.checkinputstreams({'parsedlines':1})
		self.checkoutputstreams(['parsedlines_delay'])

	def _tominutes(self, timestr):
		return reduce(lambda x, s: int(x)*60+int(s), timestr.split(':'))

	def run(self):
		while True:
			parsedline = self.read('parsedlines')
			if parsedline == None:
				break
			planned = self._tominutes(parsedline['planned_arrival'])
			defacto = self._tominutes(parsedline['defacto_arrival'])
			delay = defacto - planned
			if delay < 0:
				delay = 0
			parsedline['delay'] = delay
			self.write('parsedlines_delay', parsedline)
		self.doneall()

class TrainStationStatsBolt(Bolt):

	"""
	Calculates train statistics for each station it stops in
	Input streams: 1 parsedlines_delay
	Output streams: trainstationstats
	"""

	def __init__(self):
		Bolt.__init__(self)
		self._statsfromtrain = {}

	def check(self):
		self.checkinputstreams({'parsedlines_delay': 1})
		self.checkoutputstreams(['trainstationstats'])

	def _adddelay(self, trainum, stationum, delay):
		if trainum not in self._statsfromtrain:
			self._statsfromtrain[trainum] = {}
		if stationum not in self._statsfromtrain[trainum]:
			self._statsfromtrain[trainum][stationum] = {\
				'avg_delay': 0.0,\
				'nr_records': 0,\
				}
		avg = self._statsfromtrain[trainum][stationum]['avg_delay']
		nr = self._statsfromtrain[trainum][stationum]['nr_records']

		self._statsfromtrain[trainum][stationum]['avg_delay'] = ((avg * nr) + delay) / (nr+1)
		self._statsfromtrain[trainum][stationum]['nr_records'] = nr + 1
		
	def run(self):
		while True:
			l = self.read('parsedlines_delay')
			if l == None:
				break
			self._adddelay(l['train_num'], l['station_num'], l['delay'])
		for trainum in self._statsfromtrain.keys():
			for stationum in self._statsfromtrain[trainum].keys():
				r = self._statsfromtrain[trainum][stationum]
				r['train_num'] = trainum
				r['station_num'] = stationum
				self.write('trainstationstats', r)
		self.doneall()



class StationsStatsBolt(Bolt):

	"""
	Calculate statistics about the stations
	Input streams: 1 parsedlines_delay
	Output streams: stationsstats
	"""

	def __init__(self):
		Bolt.__init__(self)
		self._statsfromstations = {}

	def _adddelay(self, parsedline):
		station = parsedline['station_num']
		stationame = parsedline['station_name']
		if station not in self._statsfromstations.keys():
			self._statsfromstations[station] = { \
				'station_num': station,\
				'staion_name': stationame,\
				'avg_delay': 0.0,\
				'nr_records': 0,\
				'max_delay': 0,
				'nr_ontime': 0\
			}
		
		delay = parsedline['delay']
		r = self._statsfromstations[station]
		r['avg_delay'] = ((r['avg_delay'] * r['nr_records']) + delay) / (r['nr_records'] + 1)
		r['nr_records'] = r['nr_records'] + 1
		if delay == 0:
			r['nr_ontime'] = r['nr_ontime'] + 1
		# record the max delay trip
		if r['max_delay'] < delay:
			r['max_delay'] = delay
			r['planned'] = parsedline['planned_arrival']
			r['defacto'] = parsedline['defacto_arrival']
			r['date'] = parsedline['date']

	def check(self):
		self.checkinputstreams({'parsedlines_delay': 1})
		self.checkoutputstreams(['stationsstats'])

	def run(self):
		while True:
			l = self.read('parsedlines_delay')
			if l == None:
				break
			self._adddelay(l)
		map(lambda x: self.write('stationsstats', x), self._statsfromstations.values())
		self.doneall()









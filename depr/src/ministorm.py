#! /usr/bin/env python

import Queue
import threading
import sys

class Stream:

	def __init__(self, label, srcbolt, dstbolt, maxsize=4096):
		self._q = Queue.Queue(maxsize)
		self.label = label
		self._isdone = False
		srcbolt.addoutputstream(self)
		dstbolt.addinputstream(self)

	def done(self):
		self._q.put(None)

	def write(self, tpl):
		if tpl == None:
			raise Exception("null tpl")
		self._q.put(tpl)

	def read(self):
		if self._isdone:
			return None
		res = self._q.get()
		if res == None:
			self._isdone = True
		return res

class Bolt(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		self._instreams = {}
		self._outstreams = {}

	def addinputstream(self, stream):
		if stream.label not in self._instreams.keys():
			self._instreams[stream.label] = []
		self._instreams[stream.label].append(stream)
		return self
	
	def addoutputstream(self, stream):
		if stream.label not in self._outstreams.keys():
			self._outstreams[stream.label] = []
		self._outstreams[stream.label].append(stream)
		return self

	def checkinputstreams(self, labels):
		if sorted(self._instreams.keys()) != sorted(labels.keys()):
			raise Exception("invalid input streams in "+str(self))
		for k in labels.keys():
			if len(self._instreams[k]) != labels[k]:
				raise Exception("invalid input streams in "+ str(self))

	def checkoutputstreams(self, labels):
		if sorted(self._outstreams.keys()) != sorted(labels):
			raise Exception("invalid output streams in "+str(self))

	def write(self, label, tpl):
		map(lambda stream: stream.write(tpl), self._outstreams[label])

	def read(self, label, index=0):
		return self._instreams[label][index].read()

	def done(self, label):
		map(lambda stream: stream.done(), self._outstreams[label])

	def doneall(self):
		map(lambda label: self.done(label), self._outstreams.keys())

	def addto(self, threadslist):
		threadslist.append(self)
		return self


class Topology:
	def __init__(self):
		self._bolts = []

	def addbolt(self, bolt):
		bolt.addto(self._bolts)
		return bolt

	def create(self):
		raise Exception("create function must be overriden")

	def calc(self):
		map(lambda x: x.check(), self._bolts)
		map(lambda x: x.start(), self._bolts)
		map(lambda x: x.join(),  self._bolts)



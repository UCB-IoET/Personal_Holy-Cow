import time
import urllib2
import sys
import msgpack
import socket
from smap.archiver.client import RepublishClient
from smap import driver, util
import pycurl,json
from StringIO import StringIO

class walkApp(driver.SmapDriver):
  
    def setup(self, opts):
        self.add_timeseries('/index', 'unit', data_type='double')
        self.add_timeseries('/rgb','unit', data_type='double')
        self.add_timeseries('/show','unit', data_type='double')
	self.archiverurl = opts.get('archiverurl', 'http://shell.storm.pm:8079')
        self.subscription_src = opts.get('subscription', 'Path= "/touch/1/src"')
        self.r1 = RepublishClient(self.archiverurl, self.cb_src, restrict = self.subscription_src)
	self.table = {}        

    def cb_src(self, points, path_src):
		print "Src callback"
        	print "Points:", points
        	print "\nData:", path_src
        	print self.table
        	src = path_src[0][0][-1] + 0.0
		curr = time.time()
               	self.add('/rgb', curr, 31.0)
		self.add('/index', curr, src + 1.0)
		time.sleep(1)
		curr = time.time()
               	self.add('/rgb', curr, 31.0)
		self.add('/index', curr, src + 0.0)
		time.sleep(1)
		curr = time.time()
               	self.add('/rgb', curr, 0.0)
		self.add('/index', curr, src - 1.0)
		time.sleep(1)
		curr = time.time()
               	self.add('/rgb', curr, 0.0)
		self.add('/index', curr, src - 2.0)
		time.sleep(1)
		self.add('/show', time.time(), 1.0)
		time.sleep(1)
		self.add('/show', time.time(), 0.0)

    def start(self):
	print "Start"
        self.r1.connect()

    def stop(self):
        print "Stop"
        self.stopping = True

        return ledList


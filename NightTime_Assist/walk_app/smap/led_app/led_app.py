import time
import urllib2
import sys
import msgpack
import socket
from smap.archiver.client import RepublishClient
from smap import driver, util


class ledApp(driver.SmapDriver):
    
    def setup(self, opts):
        self.index = 0
	self.color_index = 0
	self.color = [992, 31, 31744]
	self.rate = float(opts.get('rate', 1))
        self.add_timeseries('/index', 'unit', data_type='double')
	self.add_timeseries('/rgb', 'unit', data_type='double')
#        self.set_metadata('/led_app', {
#                          'Metadata/Description' : 'Application to link PIR to LED',
#                         })

	self.archiverurl = opts.get('archiverurl','http://shell.storm.pm:8079')                                                
        self.subscription1 = opts.get('subscription','Path= "/PIR_SENSORS/1/PIR"')
	self.subscription2 = opts.get('subscription','Path= "/PIR_SENSORS/2/PIR"')
	self.subscription3 = opts.get('subscription','Path= "/PIR_SENSORS/3/PIR"')
        self.r1 = RepublishClient(self.archiverurl, self.cb1, restrict=self.subscription1) 
	self.r2 = RepublishClient(self.archiverurl, self.cb2, restrict=self.subscription2) 
	self.r3 = RepublishClient(self.archiverurl, self.cb3, restrict=self.subscription3)                                        

    def cb1(self, points, pir_value):
        print points, pir_value
	print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
	if pir_value[0][0][-1] == 1:
		rgb = 32767
	#	for x in range(0, 2):
		curr_time = time.time()
		self.add('/index',curr_time, 5.0)
		self.add('/rgb', curr_time, rgb+0.0)
#		time.sleep(1)

	else:
		rgb = 0.0
	#	for x in range(0, 2):
		curr_time = time.time()
		self.add('/index',curr_time, 5.0)
		self.add('/rgb', curr_time, rgb+0.0)
#		time.sleep(1)

    def cb2(self, points, pir_value):
        print points, pir_value
	print "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"
	if pir_value[0][0][-1] == 1:
		rgb = 32767
	#	for x in range(2, 4):
		curr_time = time.time()
		self.add('/index',curr_time, 10.0)
		self.add('/rgb', curr_time, rgb+0.0)
#			time.sleep(1)
	else:
		rgb = 0.0
#		for x in range(2, 4):
		curr_time = time.time()
		self.add('/index',curr_time, 10.0)
		self.add('/rgb', curr_time, rgb+0.0)
#			time.sleep(1)

    def cb3(self, points, pir_value):
 	print points, pir_value
	print "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC"
	if pir_value[0][0][-1] == 1:
		rgb = 32767
#		for x in range(4, 6):
		curr_time = time.time()
		self.add('/index',curr_time, 15.0)
		self.add('/rgb', curr_time, rgb+0.0)
#			time.sleep(1)
	else:
		rgb = 0.0
#		for x in range(4, 6):
		curr_time = time.time()
		self.add('/index',curr_time, 15.0)
		self.add('/rgb', curr_time, rgb+0.0)
#			time.sleep(1)
    
    def start(self):
	self.r1.connect()
	self.r2.connect()
	self.r3.connect()

    def stop(self):
     print "Quit"
     self.stopping = True

















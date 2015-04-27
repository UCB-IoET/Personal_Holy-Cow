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
        self.subscription = opts.get('subscription','Metadata/Sourcename = "PIR Sensor Driver"')
        self.r = RepublishClient(self.archiverurl, self.cb, restrict=self.subscription)                                        

    def cb(self, points, pir_value):
        print points, pir_value
	if pir_value[0][0][-1] == 1:
		rgb = self.color[self.color_index]
		curr_time = time.time()
		self.add('/index',curr_time, self.index+0.0)
		self.add('/rgb', curr_time, rgb+0.0)
		self.index = (self.index + 1) % 50
		self.color_index = (self.color_index + 1) % 3
    
    def start(self):
	self.r.connect()

    def stop(self):
     print "Quit"
     self.stopping = True















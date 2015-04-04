import time
import urllib2
import sys
import msgpack
import socket
from smap.archiver.client import RepublishClient
from smap import driver, util


class ledDriver(driver.SmapDriver):
    
    def setup(self, opts):
        self.rate = float(opts.get('rate', 1))
#        self.add_timeseries('/index', 'unit', data_type='double')
	self.add_timeseries('/rgb', 'unit', data_type='double')

#        self.set_metadata('/led_app', {
#                          'Metadata/Description' : 'Application to link PIR to LED',
#                         })

	self.archiverurl = opts.get('archiverurl','http://shell.storm.pm:8079')                                                
        self.subscription = opts.get('subscription','Metadata/SourceName = "LED Data Stream"')
        self.r = RepublishClient(self.archiverurl, self.cb, restrict=self.subscription)                                        

    def cb(self, points, led_index ):
        print "Points: ",points
	print "\nData" , led_index

	print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
#	index = led_index[0][0][-1] + 0.0
	rgb = led_index[0][0][-1] + 0.0
	
	curr_time = time.time()
#	self.add('/index',curr_time, index)
	self.add('/rgb', curr_time, rgb)
    
    def start(self):
	self.r.connect()

    def stop(self):
     print "Quit"
     self.stopping = True















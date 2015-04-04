import time
import urllib2
import sys
import msgpack
import socket
from smap.archiver.client import RepublishClient
from smap import driver, util


class ledApp(driver.SmapDriver):
    
    def setup(self, opts):
        self.rate = float(opts.get('rate', 1))
        #self.add_timeseries('/index', 'unit', data_type='double')
	self.add_timeseries('/rgb', 'unit', data_type='double')
        #add_timeseries(self, path, *args, **kwargs):

#        self.set_metadata('/led_app', {
#                          'Metadata/Description' : 'Application to link PIR to LED',
#                         })

	self.archiverurl = opts.get('archiverurl','http://shell.storm.pm:8079')                                                
        self.subscription = opts.get('subscription','Metadata/SourceName = "Passive Infrared Motion Sensor Driver"')
        self.r = RepublishClient(self.archiverurl, self.cb, restrict=self.subscription)                                        

    def cb(self, points, pir_value):
        print points, pir_value
	index = pir_value[0][0][-1] + 0.0
	rgb = ((31 << 10) | (31 << 5) | 31) + 0.0
	curr_time = time.time()
	self.add('/rgb',curr_time, rgb)
	#self.add('/index', curr_time, index)
    
    def start(self):
	self.r.connect()

    def stop(self):
     print "Quit"
     self.stopping = True















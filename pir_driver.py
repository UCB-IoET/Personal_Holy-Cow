import time
import urllib2
import StringIO
import RPi.GPIO as GPIO
import sys
import time
import msgpack
import socket
from smap import driver, util


class PIRDriver(driver.SmapDriver):
    
    def setup(self, opts):
        self.rate = float(opts.get('rate', 1))
        self.add_timeseries('/PIR', 'unit', data_type='double')
        #add_timeseries(self, path, *args, **kwargs):
        self.set_metadata('/PIR', {
                          'Metadata/Description' : 'Passive Infrared Motion Detector',
                          })
	# This is what we are listening on for messages
	UDP_IP = "::" #all IPs
	UDP_PORT = 1236 
 
	# Note we are creating an INET6 (IPv6) socket
	self.sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
	self.sock.bind((UDP_IP, UDP_PORT))
    
    def start(self):
        util.periodicSequentialCall(self.read).start(self.rate)
    
    def read(self):
        data, addr = self.sock.recvfrom(1024)
        pir_val = msgpack.unpackb(data)
 	self.add('/PIR', time.time(), pir_val)

    def stop(self):
     print "Quit"
     self.stopping = True















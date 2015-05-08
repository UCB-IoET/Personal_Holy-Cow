import time
import urllib2
import sys
import msgpack
import socket
from smap import driver, util


class touchDriver(driver.SmapDriver):
    
    def setup(self, opts):
        self.add_timeseries('/src', 'unit', data_type='double')
	self.add_timeseries('/dst', 'unit', data_type='double')
	# This is what we are listening on for messages
	UDP_IP = "::" #all IPs
	UDP_PORT = 1236 
 
	# Note we are creating an INET6 (IPv6) socket
	self.sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
	self.sock.bind((UDP_IP, UDP_PORT))
    
    def start(self):
	print "START"
        util.periodicSequentialCall(self.read).start(1)
    
    def read(self):
	print "READ"
        data, addr = self.sock.recvfrom(1024)
	print "\nRECEIVED: ", data, addr
        touch_data = msgpack.unpackb(data)
	print touch_data
	print "\nsrc", touch_data[0]
	print "\ndst", touch_data[1]
 	self.add('/src', time.time(), touch_data[0]+0.0)
	self.add('/dst', time.time(), touch_data[1]+0.0)

    def stop(self):
     print "Quit"
     self.stopping = True















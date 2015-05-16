import time
import urllib2
import sys
import msgpack
import socket
from smap import driver, util


class PIRDriver(driver.SmapDriver):
    
    def setup(self, opts):
        self.id = float(opts.get('id', 1))
        self.add_timeseries('/PIR', 'unit', data_type='double')
        #add_timeseries(self, path, *args, **kwargs):
        self.set_metadata('/PIR', {
                          'Metadata/Description' : 'Passive Infrared Motion Detector',
                          })
	# This is what we are listening on for messages
	UDP_IP = "::" #all IPs
	UDP_PORT = int(opts.get('port', 1236)) 
 
	# Note we are creating an INET6 (IPv6) socket
	self.sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
	self.sock.bind((UDP_IP, UDP_PORT))
    
    def start(self):
	print "START"
        util.periodicSequentialCall(self.read).start(1)
    
    def read(self):
	print "READ"
	self.add('/PIR', time.time(), 0.0)
	data, addr = self.sock.recvfrom(1024)
	print "\nRECEIVED: ", data, addr
        pir_data = msgpack.unpackb(data)
	print pir_data
	print "\nID", pir_data[0]
	print "\nPIR_VALUE", pir_data[1]
 	if (pir_data[0] == self.id):
		self.add('/PIR', time.time(), pir_data[1]+0.0)

    def stop(self):
     print "Quit"
     self.stopping = True















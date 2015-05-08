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
        self.add_timeseries('/index', 'unit', data_type='double')
	self.add_timeseries('/rgb', 'unit', data_type='double')
	self.archiverurl = opts.get('archiverurl','http://shell.storm.pm:8079')                                                
        self.subscription_index = 'uuid = "25c9c94c-b965-5d52-befd-ef9c01e1c4f1"'
        self.subscription_rgb = 'uuid = "e994a394-f6e5-59eb-a80a-bf47d8fceeca"'
        self.subscription_show = 'uuid = "30e232f5-d728-53d4-bab5-feaa8f09dfcd"'
        #self.subscription_index = 'Path= "/led_driver_new/1/index"'
	#self.subscription_rgb = 'Path= "/led_driver_new/1/rgb"'
	#self.subscription_show = 'Path= "/led_driver_new/1/show"'
        self.r1 = RepublishClient(self.archiverurl, self.cb_index, restrict=self.subscription_index) 
	self.r2 = RepublishClient(self.archiverurl, self.cb_rgb, restrict=self.subscription_rgb)  
	self.r3 = RepublishClient(self.archiverurl, self.cb_show, restrict=self.subscription_show)
	# Table to store data to be sent
	self.table = {} 
	# Create socket
	self.UDP_IP = "2001:470:832b:2:212:6d02::304f" #all IPs
	self.UDP_PORT = 1444 
	self.sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

    def cb_index(self, points, led_index ):
        print "Points: ",points
	print "\nData" , led_index
	print "CALLBACK INDEX"
	print led_index
	for pair in led_index[0]:
            print "PAIR: ", pair
	    index = pair[-1] + 0.0
	    curr_time = time.time()
	    self.add('/index', curr_time, index)
	    print(pair[-2])
	    if (pair[-2] not in self.table.keys()):
	        self.table[pair[-2]] = {}
            self.table[pair[-2]][0] = index

    def cb_rgb(self, points, led_rgb ):
        print "Points: ",points
	print "\nData" , led_rgb
	print "RGB CALLBACK"
	print led_rgb
	for pair in led_rgb[0]:
            rgb = pair[-1] + 0.0
	    curr_time = time.time()
	    self.add('/rgb', curr_time, rgb)
	    print(pair[-2])
	    if (pair[-2] not in self.table.keys()):
	        self.table[pair[-2]] = {}
	    self.table[pair[-2]][1] = rgb

    def cb_show(self, points, led_show ):
	print "Points: ",points
	print "\nData" , led_show
	print "SHOW CALLBACK"
	print led_show
	for pair in led_show[0]:
	    show = pair[-1]
	    if (show == 1):
	        while len(self.table.keys()) > 0:
		    self.send_rgb()
		    time.sleep(0.5)
	            msg = {}
	            msg["type"] = "display"
	            print msg
	            msg_pack = msgpack.packb(msg)
	            print "SENDING DISPLAYYYYYYYYY" 
                    self.sock.sendto(msg_pack, (self.UDP_IP, self.UDP_PORT))

    def send_rgb(self):
	print "Sending data to led strip"
	print self.table
	if (len(self.table.keys()) > 0):
		earliest_time = min(self.table, key=self.table.get)
		index = self.table[earliest_time][0]
		rgb = self.table[earliest_time][1]
		del self.table[earliest_time]
		msg = {}
		msg["type"] = "set"
		msg["index"] = index
		msg["rgb"] = rgb
		print msg
		msg_pack = msgpack.packb(msg)
		print "sending"
		for i in range(0,5):
                    print("SENDING RRRRRRRRRRRRRRRRRRRR")
		    print(self.sock.sendto(msg_pack, (self.UDP_IP, self.UDP_PORT)))
                    time.sleep(0.5)
	

    def start(self):
	self.r1.connect()
	self.r2.connect()
	self.r3.connect()
	#util.periodicSequentialCall(self.send_rgb).start(1)

    def stop(self):
     print "Quit"
     self.stopping = True















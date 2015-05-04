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
        self.subscription_index = 'Path= "/led_driver/1/index"'
	self.subscription_rgb = 'Path= "/led_driver/1/rgb"'
	self.subscription_show = 'Path= "/led_driver/1/show"'
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
	print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
	print self.table
	index = led_index[0][0][-1] + 0.0
	curr_time = time.time()
	self.add('/index', curr_time, index)
	print(led_index[0][0][-2])
	if (led_index[0][0][-2] not in self.table.keys()):
		self.table[led_index[0][0][-2]] = {}
	self.table[led_index[0][0][-2]][0] = index

    def cb_rgb(self, points, led_rgb ):
        print "Points: ",points
	print "\nData" , led_rgb
	print "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"
	rgb = led_rgb[0][0][-1] + 0.0
	curr_time = time.time()
	self.add('/rgb', curr_time, rgb)
	print(led_rgb[0][0][-2])
	if (led_rgb[0][0][-2] not in self.table.keys()):
		self.table[led_rgb[0][0][-2]] = {}
	self.table[led_rgb[0][0][-2]][1] = rgb

    def cb_show(self, points, led_show ):
	print "Points: ",points
	print "\nData" , led_show
	print "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD"
	show = led_show[0][0][-1]
	if (show == 1):
		msg = {}
		msg["type"] = "display"
		print msg
		msg_pack = msgpack.packb(msg)
		self.sock.sendto(msg_pack, (self.UDP_IP, self.UDP_PORT))

    def send_rgb(self):
	print "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC"
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
		print(self.sock.sendto(msg_pack, (self.UDP_IP, self.UDP_PORT)))
	

    def start(self):
	self.r1.connect()
	self.r2.connect()
	self.r3.connect()
	util.periodicSequentialCall(self.send_rgb).start(1)

    def stop(self):
     print "Quit"
     self.stopping = True















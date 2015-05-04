import time
import urllib2
import sys
import msgpack
import socket
import json
import requests
from client import RepublishClient
from smap import util
from twisted.internet import reactor

archiverurl = 'http://shell.storm.pm:8079'
archiveraddurl = 'http://shell.storm.pm:8079/add/apikeyhere'
rate = 1
subscription_index = 'Path= "/led_driver/1/index"'
subscription_rgb = 'Path= "/led_driver/1/rgb"'
subscription_show = 'Path= "/led_driver/1/show"'
indexpath = 'led_output/1/index'
rgbpath = '/led_output/1/rgb'
showpath = '/led_output/1/show'
# Table to store data to be sent
table={}
# Create socket
UDP_IP = "2001:470:832b:2:212:6d02::304f" #all IPs
UDP_PORT = 1444
sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

index = {indexpath : {
            'Metadata': {
                'Sourcename': "LED Path App Stream",
                'Data': "Random Length Vector"
            },
            'Properties': {
                "UnitofMeasure": "vector",
                "UnitofTime": "s",
                "StreamType": "object"
            },
            'Readings': [],
            'uuid': '19203a86-ec58-11e4-953c-5cc5d4ded1a',
        },
        }
rgb = {rgbpath : {
            'Metadata': {
                'Sourcename': "LED Path App Stream",
                'Data': "Random Length Vector"
            },
            'Properties': {
                "UnitofMeasure": "vector",
                "UnitofTime": "s",
                "StreamType": "object"
            },
            'Readings': [],
            'uuid': '19203a86-ec58-11e4-953c-5cc5d4ded1d',
        },
        }

def cb_index(points, led_index):
    print "INDEX CALLBACK"
    print "Points: ",points
    print "\nData" , led_index
    print table
    indexvalue = led_index[0][0][-1]
    print indexvalue
    now = int(time.time())
    index[indexpath]['Readings'] = [[now, indexvalue]]
    print(requests.post(archiveraddurl, data = json.dumps(index)))
    print(led_index[0][0][-2])
    if (led_index[0][0][-2] not in table.keys()):
        table[led_index[0][0][-2]] = {}
    table[led_index[0][0][-2]][0] = index

def cb_rgb(points, led_rgb):
    print "RGB CALLBACK"
    print "Points: ",points
    print "\nData" , led_rgb
    rgbvalue = led_rgb[0][0][-1]
    print rgbvalue
    now = int(time.time())
    rgb[rgbpath]['Readings'] = [[now, rgbvalue]]
    print(led_rgb[0][0][-2])
    print(requests.post(archiveraddurl, data = json.dumps(rgb)))
    if (led_rgb[0][0][-2] not in table.keys()):
        table[led_rgb[0][0][-2]] = {}
    table[led_rgb[0][0][-2]][1] = rgb

def cb_show(points, led_show ):
    print "SHOW CALLBACK"
    print "Points: ",points
    print "\nData" , led_show
    show = led_show[0][0][-1]
    if (show == 1):
        msg = {}
        msg["type"] = "display"
        print msg
        msg_pack = msgpack.packb(msg)
        sock.sendto(msg_pack, (UDP_IP, UDP_PORT))

def send_rgb():
    print "Sending data to led strip"
    print table
    if (len(table.keys()) > 0):
        earliest_time = min(table, key=table.get)
	print earliest_time
        index = table[earliest_time][0]
        rgb = table[earliest_time][1]
        del table[earliest_time]
        msg = {}
        msg["type"] = "set"
        msg["index"] = index
        msg["rgb"] = rgb
        print msg
        msg_pack = msgpack.packb(msg)
        print "sending"
        print(sock.sendto(msg_pack, (UDP_IP, UDP_PORT)))

r1 = RepublishClient(archiverurl, cb_index, restrict=subscription_index) 
r2 = RepublishClient(archiverurl, cb_rgb, restrict=subscription_rgb)  
r3 = RepublishClient(archiverurl, cb_show, restrict=subscription_show)
r1.connect()
r2.connect()
r3.connect()
util.periodicSequentialCall(send_rgb).start(1)

reactor.run()

import time
import urllib2,httplib
import sys
import msgpack
import socket
from smap.archiver.client import RepublishClient
from smap import driver, util
import pycurl,json
from StringIO import StringIO
import Queue

class ledDriver(driver.SmapDriver):
    
    def setup(self, opts):
        self.rate = float(opts.get('rate', 1))
        self.add_timeseries('/index', 'unit', data_type='double')
	self.add_timeseries('/rgb', 'unit', data_type='double')
        
	self.archiverurl = opts.get('archiverurl','http://shell.storm.pm:8079')                                                
        self.subscription_index = opts.get('subscription','Path= "/led_app/1/index"')
	self.subscription_rgb = opts.get('subscription','Path= "/led_app/1/rgb"')
        self.r1 = RepublishClient(self.archiverurl, self.cb_index, restrict=self.subscription_index) 
	self.r2 = RepublishClient(self.archiverurl, self.cb_rgb, restrict=self.subscription_rgb)  
	self.table = {} 

	self.UDP_IP = "2001:470:4956:2:212:6d02::304f" #all IPs
	self.UDP_PORT = 1444 
 
	# Note we are creating an INET6 (IPv6) socket
	self.sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
	
	#excute curl request to get metadata with led path
	storage = StringIO()
	url = "http://shell.storm.pm:8079/api/query"
	data = "select * where Metadata/Sourcename = 'LED Model Driver'"
	c = pycurl.Curl()
	c.setopt(pycurl.URL, url)
	c.setopt(c.WRITEFUNCTION, storage.write)
	c.setopt(pycurl.POST, 1)
	c.setopt(pycurl.POSTFIELDS, data)
	data =  c.perform()
	c.close()
	self.adjList = {}
	content = json.loads(storage.getvalue())	
    	self.createAdjacencyList(content[-1]['Metadata']['AdjacencyList'])

	#For testing
	print "1 to 6"
	print(self.getLedIndices(1,6))
	print "\n1 to 3"
	print(self.getLedIndices(1,3))
	print "\n8 to 1"
	print(self.getLedIndices(8,1))
	print "\n10 to 1"
	print(self.getLedIndices(10, 1))
	print "\n5 to 18"
	print(self.getLedIndices(5, 18))
	print "\n9 to 14"
	print(self.getLedIndices(9, 14))
	print "\n1 to 2"
        print(self.getLedIndices(1,2))
	print "\n9 to 11"
	print(self.getLedIndices(9, 11))
	print "\n17 to 18"
	print(self.getLedIndices(17,18))
	print "\n18 to 17"
	print(self.getLedIndices(18,17))

    def createAdjacencyList(self, metadata):
	for key, value in metadata.iteritems():
		value_list = [x.strip() for x in value.split(',')]
		self.adjList[key] = value_list;

    def getLedIndices(self, start, end):
	path = self.getPath(start, end)
	print path
	ledList = []
	if(len(path) == 1):
		rangeStart = start if start <= end else end
		rangeEnd = end if start <=end else start
		ledList.extend(range(rangeStart, rangeEnd+1))
	elif (len(path) > 1):
        	ledList.extend(self.getIndicesSubrange(start, path[0]))
		for i in range(1, len(path)-1):
			rangeValue = [int(x) for x in path[i].split('-')]
			ledList.extend(range(rangeValue[0], rangeValue[1]+1))
        	ledList.extend(self.getIndicesSubrange(end, path[len(path)-1]))
	return ledList

    def getIndicesSubrange(self, index, rangeList):
	if '-' in rangeList:
		rangeValue = [int(x) for x in rangeList.split('-')]
		if (abs(index - rangeValue[0]) < abs(rangeValue[1] - index)):
                	rangeStart = rangeValue[0]
                	rangeEnd = index
        	else:
                	rangeStart = index
                	rangeEnd = rangeValue[1]
	elif '_' in rangeList:
		rangeValue = [int(x) for x in rangeList.split('_')]
		rangeStart = index if index <= rangeValue[0] else rangeValue[0]
		rangeEnd = rangeValue[0] if index <= rangeValue[0] else index
	return range(rangeStart, rangeEnd+1)

    def getPath(self, start, end):
	queue = []
	for key in self.adjList.keys():
		if (self.indexInRange(start, key)):
			queue.append([key])
			break
	visited = set()
	while queue:
		path = queue.pop(0)
		vertex = path[-1]
		if (self.indexInRange(end, vertex)):
			return path
		elif vertex not in visited:
			for currNeighbor in self.adjList.get(vertex, []):
				newPath = list(path)
				newPath.append(currNeighbor)
				queue.append(newPath)
			visited.add(vertex)
	return []

    def indexInRange(self, index, rangeToCheck):
	if '-' in rangeToCheck:
		splitRange = [int(x) for x in rangeToCheck.split('-')]
	elif '_' in rangeToCheck:
                splitRange = [int(x) for x in rangeToCheck.split('_')]
	start = splitRange[0] if splitRange[0] <= splitRange[1] else splitRange[1]
	end = splitRange[1] if splitRange[0] <= splitRange[1] else splitRange[0]
	if (index >= start and index <= end):
		return True 
        return False

    def cb_index(self, points, led_index ):
        print "Points: ",points
	print "\nData" , led_index

	print self.table
#	index = led_index[0][0][-1] + 0.0
	index = led_index[0][0][-1] + 0.0
	
	curr_time = time.time()
#	self.add('/index',curr_time, index)
	self.add('/index', curr_time, index)
	if (led_index[0][0][-2] not in self.table.keys()):
		self.table[led_index[0][0][-2]] = {}
	self.table[led_index[0][0][-2]][0] = index

    def cb_rgb(self, points, led_rgb ):
        print "Points: ",points
	print "\nData" , led_rgb

#	index = led_index[0][0][-1] + 0.0
	rgb = led_rgb[0][0][-1] + 0.0
	
	curr_time = time.time()
#	self.add('/index',curr_time, index)
	self.add('/rgb', curr_time, rgb)
	if (led_rgb[0][0][-2] not in self.table.keys()):
		self.table[led_rgb[0][0][-2]] = {}
	self.table[led_rgb[0][0][-2]][1] = rgb

    def send_rgb(self):
	print "Sending data to led strip"
	if (len(self.table.keys()) > 0):
		earliest_time = min(self.table, key=self.table.get)
		index = self.table[earliest_time][0]
		rgb = self.table[earliest_time][1]
		del self.table[earliest_time]
		msg = {}
		msg["index"] = index
		msg["rgb"] = rgb
		print msg
		msg_pack = msgpack.packb(msg)
		self.sock.sendto(msg_pack, (self.UDP_IP, self.UDP_PORT))
	

    def start(self):
	self.r1.connect()
	self.r2.connect()
	util.periodicSequentialCall(self.send_rgb).start(1)

    def stop(self):
     print "Quit"
     self.stopping = True















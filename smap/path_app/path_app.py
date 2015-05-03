import time
import urllib2
import sys
import msgpack
import socket
from smap.archiver.client import RepublishClient
from smap import driver, util
import pycurl,json
from StringIO import StringIO

class pathApp(driver.SmapDriver):
  
    def setup(self, opts):
        self.index = 0
        self.color = [992, 31, 31744]
        self.rate = float(opts.get('rate', 1))
        self.add_timeseries('/index', 'unit', data_type='double')
        self.add_timeseries('/rgb','unit', data_type='double')
        self.add_timeseries('/show','unit', data_type='double')
	self.archiverurl = opts.get('archiverurl', 'http://shell.storm.pm:8079')
        self.subscription_src = opts.get('subscription', 'Path= "/touch/1/src"')
        self.subscription_dst = opts.get('subscription', 'Path  = "/touch/1/dst"')
        self.r1 = RepublishClient(self.archiverurl, self.cb_src, restrict = self.subscription_src)
        self.r2 = RepublishClient(self.archiverurl, self.cb_dst, restrict = self.subscription_dst)
	self.table = {}        
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
        self.createAdjacencyList(content[0]['Metadata']['AdjacencyList'])
	print content
	print self.getLedIndices(1, 9);

    def cb_src(self, points, path_src):
	print "Src callback"
        print "Points:", points
        print "\nData:", path_src
        print self.table
        src = path_src[0][0][-1] + 0.0
        curr_time= time.time()
        #self.add('/src', curr_time, src)
        if (path_src[0][0][-2] not in self.table.keys()):
                self.table[path_src[0][0][-2]] = {}
        self.table[path_src[0][0][-2]][0] = src
    
    def cb_dst(self, points, path_dst):
	print "Dst callback"
        print "Points:", points
        print "\nData:", path_dst
        print self.table
        dst = path_dst[0][0][-1] + 0.0
        curr_time= time.time()
        #self.add('/dst', curr_time, dst)
        if (path_dst[0][0][-2] not in self.table.keys()):
                self.table[path_dst[0][0][-2]] = {}
        self.table[path_dst[0][0][-2]][1] = dst

    def sendPath(self):
        print "Sending data to led driver"
	print self.table
        if (len(self.table.keys()) > 0):
                earliest_time = min(self.table, key=self.table.get)
                src = self.table[earliest_time][0]
                dst = self.table[earliest_time][1]
                del self.table[earliest_time]
		path = self.getLedIndices(int(src), int(dst))
		for index in path:
			print(index)
			curr = time.time()
                	self.add('/rgb', curr, 31 + 0.0)
			self.add('/index', curr, index + 0.0)
			time.sleep(1)
		self.add('/show', time.time(), 1.0)
		time.sleep(1)
		self.add('/show', time.time(), 0.0)

    def start(self):
	print "Start"
        self.r1.connect()
        self.r2.connect()
        util.periodicSequentialCall(self.sendPath).start(1)

    def stop(self):
        print "Stop"
        self.stopping = True

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

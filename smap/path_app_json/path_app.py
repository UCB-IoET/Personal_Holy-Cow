import time
import urllib2
import sys
import msgpack
import socket
from smap.archiver.client import RepublishClient
import pycurl,json
from StringIO import StringIO

archiverurl = 'http://shell.storm.pm:8079'
subscription_src = 'Path= "/touch/1/src"'
subscription_dst = 'Path  = "/touch/1/dst"'
table = {}
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
adjList = {}
content = json.loads(storage.getvalue())

def cb_src(points, path_src):
	print "Src callback"
    print "Points:", points
    print "\nData:", path_src
    print table
    src = path_src[0][0][-1] + 0.0
    curr_time= time.time()
    #self.add('/src', curr_time, src)
    if (path_src[0][0][-2] not in self.table.keys()):
        table[path_src[0][0][-2]] = {}
    table[path_src[0][0][-2]][0] = src
    
def cb_dst(points, path_dst):
	print "Dst callback"
    print "Points:", points
    print "\nData:", path_dst
    print table
    dst = path_dst[0][0][-1] + 0.0
    curr_time= time.time()
    #self.add('/dst', curr_time, dst)
    if (path_dst[0][0][-2] not in table.keys()):
        table[path_dst[0][0][-2]] = {}
    table[path_dst[0][0][-2]][1] = dst

def sendPath():
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
		curr = time.time()]
		time.sleep(1)
	self.add('/show', time.time(), 1.0)
	time.sleep(1)
	self.add('/show', time.time(), 0.0)

def createAdjacencyList(metadata):
    for key, value in metadata.iteritems():
            value_list = [x.strip() for x in value.split(',')]
            adjList[key] = value_list;

def getLedIndices(start, end):
    path = getPath(start, end)
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
            ledList.extend(getIndicesSubrange(end, path[len(path)-1]))
    return ledList

def getIndicesSubrange(index, rangeList):
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

def getPath(start, end):
    queue = []
    for key in adjList.keys():
            if (indexInRange(start, key)):
                    queue.append([key])
                    break
    visited = set()
    while queue:
            path = queue.pop(0)
            vertex = path[-1]
            if (indexInRange(end, vertex)):
                    return path
            elif vertex not in visited:
                    for currNeighbor in adjList.get(vertex, []):
                            newPath = list(path)
                            newPath.append(currNeighbor)
                            queue.append(newPath)
                    visited.add(vertex)
    return []

def indexInRange(index, rangeToCheck):
    if '-' in rangeToCheck:
            splitRange = [int(x) for x in rangeToCheck.split('-')]
    elif '_' in rangeToCheck:
            splitRange = [int(x) for x in rangeToCheck.split('_')]
    start = splitRange[0] if splitRange[0] <= splitRange[1] else splitRange[1]
    end = splitRange[1] if splitRange[0] <= splitRange[1] else splitRange[0]
    if (index >= start and index <= end):
            return True
    return False


r1 = RepublishClient(archiverurl, cb_src, restrict = subscription_src)
r2 = RepublishClient(archiverurl, cb_dst, restrict = subscription_dst)
r1.connect()
r2.connect()
util.periodicSequentialCall(sendPath).start(1)
createAdjacencyList(content[0]['Metadata']['AdjacencyList'])
print content
print getLedIndices(1, 9);

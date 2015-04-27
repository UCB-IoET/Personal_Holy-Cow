import time
import urllib2
import sys
import msgpack
import socket
from smap.archiver.client import RepublishClient
from smap import driver, util

class pathApp(driver.SmapDriver):
  
    def setup(self, opts):
        self.index = 0
        self.color = [992, 31, 31744]
        self.rate = float(opts.get('rate', 1))
        self.add_timeseries('/index', 'unit', data_type='double')
        self.add_timeseries('/rgb','unit', data_type='double')
        self.archiverurl = opts.get('archiverurl', 'http://shell.storm.pm:8079')
        self.subscription_src = opts.get('subscription', 'Path= "touch/1/src"')
        self.subscription_dst = opts.get('subscription', 'Path  = "touch/1/dst"')
        self.r1 = RepublishClient(self.archiverurl, self.cb_src, restrict = self.subscription_src)
        self.r2 = RepublishClient(self.archiverurl, self.cb_dst, restrict = self.subscription_dst)

    def cb_src(self, points, path_src)
        print "Points:", points
        print "\nData:", path_src
        print self.table
        src = path_src[0][0][-1] + 0.0
        curr_time= time.time()
        self.add('/src', curr_time, src)
    
    def cb_dst(self, points, path_dst)
        print "Points:", points
        print "\nData:", path_dst
        print self.table
        dst = path_dst[0][0][-1] + 0.0
        curr_time= time.time()
        self.add('/dst', curr_time, dst)

    def start(self):
        self.r1.connect()
        self.r2.connect()

    def stop(self)
        print "Quit"
        self.stopping = True


from smap import driver
from smap.archiver.client import RepublishClient
import time

class ledDriver(driver.SmapDriver):
	def setup(self, opts):
		self.add_timeseries('/command1', 'unit', data_type='double')
		self.add_timeseries('/command2', 'unit', data_type='double')
		print self
		#self.set_metadata('/command', {'Metadata/override':'4c93ec25-c0c0-5261-94d1-c2080857fa59'})
		self.archiverurl = opts.get('archiverurl','http://shell.storm.pm:8079')
		self.subscription = opts.get('subscription','Metadata/Sourcename = "LED Data Stream"')
		self.r = RepublishClient(self.archiverurl, self.cb, restrict=self.subscription)

	def cb(self, points, data):
		print "Callback"
		print points, data
		curr_time= time.time()
		#index= data[0][0][-1]
		index = 4.0
		rgb= 32151.0
		#rgb= data[0][0][-2]
		self.add('/command1', curr_time, index)
		self.add('/command2', curr_time, rgb)
	
	def start(self):
		print self
		print "Start function"
		self.r.connect()
	
	def stop(self):
		print "Quit"
		self.stopping = True

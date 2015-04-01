require("storm")
require("cord")
calibrationTime=30
local PIR={}

function PIR:new(ledpin)
	
	assert(ledpin and storm.io[ledpin], "invalid pin spec")
	obj = {pin = ledpin}
	setmetatable(obj, self)
	self.__index=self
	storm.io.set_mode(storm.io.INPUT, storm.io[ledpin])
	storm.io.set(0, storm.io[ledpin])
	print("Calibrating Sensor")
	cord.new(function()
		for i=0, calibrationTime do
			cord.await(storm.os.invokeLater, storm.os.SECOND)
			print(".")
		end
		print("Done calibrating") 
		cord.await(storm.os.invokeLater, 50*storm.os.MILLISECOND)
		return obj
	end)
end

function PIR:sense()
	cord.new(function()

		cord.await(storm.os.invokeLater, storm.os.SECOND)
		return (storm.io.get(storm.io[self.pin]))
	end)
end

return PIR

	

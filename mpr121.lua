REG = require "i2creg"
bit = require "bit"

local codes = {
    MPR121_I2CADDR_DEFAULT = 0x5A,
	MPR121_TOUCHSTATUS_L   = 0x00,
	MPR121_TOUCHSTATUS_H   = 0x01,
	MPR121_FILTDATA_0L     = 0x04,
	MPR121_FILTDATA_0H     = 0x05,
	MPR121_BASELINE_0      = 0x1E,
	MPR121_MHDR            = 0x2B,
	MPR121_NHDR            = 0x2C,
	MPR121_NCLR            = 0x2D,
	MPR121_FDLR            = 0x2E,
	MPR121_MHDF            = 0x2F,
	MPR121_NHDF            = 0x30,
	MPR121_NCLF            = 0x31,
	MPR121_FDLF            = 0x32,
	MPR121_NHDT            = 0x33,
	MPR121_NCLT            = 0x34,
	MPR121_FDLT            = 0x35,

	MPR121_TOUCHTH_0       = 0x41,
	MPR121_RELEASETH_0     = 0x42,
	MPR121_DEBOUNCE        = 0x5B,
	MPR121_CONFIG1         = 0x5C,
	MPR121_CONFIG2         = 0x5D,
	MPR121_CHARGECURR_0    = 0x5F,
	MPR121_CHARGETIME_1    = 0x6C,
	MPR121_ECR             = 0x5E,
	MPR121_AUTOCONFIG0     = 0x7B,
	MPR121_AUTOCONFIG1     = 0x7C,
	MPR121_UPLIMIT         = 0x7D,
	MPR121_LOWLIMIT        = 0x7E,
	MPR121_TARGETLIMIT     = 0x7F,

	MPR121_GPIODIR         = 0x76,
	MPR121_GPIOEN          = 0x77,
	MPR121_GPIOSET         = 0x78,
	MPR121_GPIOCLR         = 0x79,
	MPR121_GPIOTOGGLE      = 0x7A,

	MPR121_SOFTRESET       = 0x80,
}

local MPR121 = {}

function MPR121:new()
   local obj = {port=storm.i2c.INT, addr = codes.MPR121_I2CADDR_DEFAULT, 
                reg=REG:new(storm.i2c.INT, codes.MPR121_I2CADDR_DEFAULT)}
   setmetatable(obj, self)
   self.__index = self
   return obj
end

function MPR121:begin()
    self.reg:w(codes.MPR121_SOFTRESET, 0x63)
    -- original code had a delay here
    self.reg:w(codes.MPR121_ECR, 0x0)

    c = self.reg:r(codes.MPR121_CONFIG2, 1)
    if (c ~= 0x24) then return false end
    self:setThreshholds(12, 6)

    self.reg:w(codes.MPR121_MHDR, 0x01)
    self.reg:w(codes.MPR121_NHDR, 0x01)
    self.reg:w(codes.MPR121_NCLR, 0x0E)
    self.reg:w(codes.MPR121_FDLR, 0x00)

    self.reg:w(codes.MPR121_MHDF, 0x01)
    self.reg:w(codes.MPR121_NHDF, 0x05)
    self.reg:w(codes.MPR121_NCLF, 0x01)
    self.reg:w(codes.MPR121_FDLF, 0x00)

    self.reg:w(codes.MPR121_NHDT, 0x00)
    self.reg:w(codes.MPR121_NCLT, 0x00)
    self.reg:w(codes.MPR121_FDLT, 0x00)

    self.reg:w(codes.MPR121_DEBOUNCE, 0)
    self.reg:w(codes.MPR121_CONFIG1, 0x10)
    self.reg:w(codes.MPR121_CONFIG2, 0x20)

    self.reg:w(codes.MPR121_ECR, 0x8F)

end

function MPR121:setThresholds(touch, release)
  for i=0,11 do
    self.reg:w(codes.MPR121_TOUCHTH_0 + 2*i, touch)
    self.reg:w(codes.MPR121_RELEASETH_0 + 2*i, release)
  end
end

function MPR121:filteredData(t)
  if (t > 12) then return 0 end
  return self.reg:r(codes.MPR121_FILTDATA_0L + t*2)
end

function MPR121:baselineData(t)
  if (t > 12) then return 0 end
  bl = self.reg:r(codes.MPR121_BASELINE_0 + t, 1)
  return bit.lshift(bl, 2)
end

function MPR121:touched()
  t = self.reg:r(codes.MPR121_TOUCHSTATUS_L, 2)
  return bit.band(t, 0x0FFF)
end

return MPR121

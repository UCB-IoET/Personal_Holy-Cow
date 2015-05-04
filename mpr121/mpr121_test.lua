bit = require "bit"
MPR121 = require "mpr121"
require "cord"
touchConnect = false

function cap_setup() 
	cord.new(function() 
	    cap = MPR121:new()
	    if (cap:begin() == 0) then
		    return false
  	    end
        while(1) do
            currtouched = cap:touched()
            for i = 0, 11 do
			    local offset = bit.lshift(1, i)
			    if (bit.band(offset, currtouched) ~= 0) then
			        print(i.."Touched!")
			    end
		    end
        end
	 end)
	return true
end

touchConnect = cap_setup()

-- enable a shell
sh = require "stormsh"
sh.start()
cord.enter_loop()


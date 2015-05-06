require "cord"
bit = require "bit"
MPR121 = require "mpr121"

shellip = "2001:470:66:3f9::2"
listen_port = 1337

--[[
coffeeIndex = 10
tvIndex = 23
bathroomIndex = 30
bookshelfIndex = 40
cradleIndex = 50
]]--

startTouchIndex = 0
endTouchIndex = 64
startLedIndex = 0


touchConnect = true

mapLedTouch = {}

sendsock = storm.net.udpsocket(listen_port, function() end)

function onconnectble(state) 
	print("IGNORE")
end

function cap_setup() 
	cord.new(function() 
	    cap1 = MPR121:new(storm.i2c.EXT,0xb4 )
	    cap2 = MPR121:new(storm.i2c.EXT, 0xb8)
	    cap3 = MPR121:new(storm.i2c.EXT, 0xba)
	    if (cap1:begin() == 0) then
    		print("MPR121 b4 not found, check wiring?")
		return false
  	    end

        if (cap2:begin() == 0) then
    		print("MPR121 b8 not found, check wiring?")
		return false
  	    end

        if (cap3:begin() == 0) then
    		print("MPR121 bA not found, check wiring?")
		return false
  	    end
	 end)
	return true
end

function touchToLed()
    mapLedTouch["b4"] = {}
    mapLedTouch["b8"] = {}
    mapLedTouch["ba"] = {}

    local curTouch = mapLedTouch["b4"]
	for i = 0, 11 do
		curTouch[i] = {}
		curTouch[i][0] = startLedIndex 
        curTouch[i][1] = startLedIndex + 1
		startLedIndex = startLedIndex + 2
	end
    
     curTouch = mapLedTouch["ba"]
    for i = 0, 11 do
		curTouch[i] = {}
		curTouch[i][0] = startLedIndex 
        curTouch[i][1] = startLedIndex + 1
		startLedIndex = startLedIndex + 2
	end

    curTouch = mapLedTouch["b8"]
    for i = 0, 11 do
        curTouch[i] = {}
		curTouch[i][0] = startLedIndex 
        curTouch[i][1] = startLedIndex + 1
		startLedIndex = startLedIndex + 2
	end

end

touchConnect = cap_setup()
--print("value of touchConnect"..touchConnect)
touchToLed()

storm.bl.enable("unused", onconnectble, function()

   local touch_handle = storm.bl.addservice(0x1343)
   char_handle = storm.bl.addcharacteristic(touch_handle, 0x1344, function(x)
		
		print("Inside"..x)
		--Destination
		local dest = tonumber(x, 16)

		--Source
		if (touchConnect == true and dest > -1) then
			local found = false
			local src = 0
			cord.new(function()
				while (1) do
					local currtouched1 = cap1:touched()
                    local currtouched2 = cap2:touched()
                    local currtouched3 = cap3:touched()

					--print("TOUCH B4"..currtouched1)
                    --print("TOUCH B8"..currtouched2)
                    --print("TOUCH bA"..currtouched3)

                    local currTouch = mapLedTouch["b4"]
					for i = 0, 11 do
						local offset = bit.lshift(1, i)
						if (bit.band(offset, currtouched1) ~= 0) then
							src = currTouch[i][0] --pick the first index
							found = true
							print("b4 "..i.." Touched!")
							break
						end
					end

					if (found == true) then
						break
					end
                    
                    currTouch = mapLedTouch["b8"]
					for i = 0, 11 do
						local offset = bit.lshift(1, i)
						if (bit.band(offset, currtouched2) ~= 0) then
							src = currTouch[i][0] --pick the first index
							found = true
							print("b8 "..i.." Touched!")
							break
						end
					end

					if (found == true) then
						break
					end

                    currTouch = mapLedTouch["ba"]
					for i = 0, 11 do
						local offset = bit.lshift(1, i)
						if (bit.band(offset, currtouched3) ~= 0) then
							src = currTouch[i][0] --pick the first index
							found = true
							print("ba "..i.." Touched!")
							break
						end
					end

					if (found == true) then
						break
					end
                    
				end

				--src = 11
				local msg = {src, dest}
				print("Sending "..src.." "..dest)
				local payload = storm.mp.pack(msg)
				storm.net.sendto(sendsock, payload, shellip, 1236)
			end)
		elseif (dest == -1) then
			print("No Device Found")
		else
			print ("Connect the Touch Sensor First Bro")
		end

   end)

	local test_handle = storm.bl.addservice(0x1341)
   char1_handle = storm.bl.addcharacteristic(test_handle, 0x1342, function(x) print("TEST") end)
end)

sh = require "stormsh"
sh.start()
cord.enter_loop()

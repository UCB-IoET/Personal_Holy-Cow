bit = require "bit"
MPR121 = require "mpr121"
require "cord"
shellip = "2001:470:66:3f9::2"
listen_port = 1337

startTouchIndex = 0
endTouchIndex = 64
startLedIndex = 0

touchConnect = true

mapLedTouch = {}

sendsock = storm.net.udpsocket(listen_port, function() end)

function touchToLed()
    print("In touchToLed")
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

function findTouched(currtouched1, currtouched2, currtouched3)
    local currTouch = mapLedTouch["b4"]
    local src = nil
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
        return src
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
        return src
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
        return src
    end
    return nil        
end

function cap_setup() 
	cord.new(function() 
	    cap1 = MPR121:new(storm.i2c.EXT,0xb4)
        print("cap1", cap1)
	    cap2 = MPR121:new(storm.i2c.EXT, 0xb8)
        print("cap2", cap2)
	    cap3 = MPR121:new(storm.i2c.EXT, 0xba)
        print("cap3", cap3)
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
        local prevSrc = nil
        while(1) do
            local currtouched1 = cap1:touched()
            local currtouched2 = cap2:touched()
            local currtouched3 = cap3:touched()
            local src = findTouched(currtouched1, currtouched2, currtouched3)
            if (src and src ~= prevSrc) then
                local dest = src
                local msg = {src, dest}
                print("Sending "..src.." "..dest)
                local payload = storm.mp.pack(msg)
                storm.net.sendto(sendsock, payload, shellip, 1236)
            end
            prevSrc = src
            src = nil
        end 
	end)
    return true
end

touchToLed()
touchConnect = cap_setup()

-- enable a shell
sh = require "stormsh"
sh.start()
cord.enter_loop()

require ("cord")
calibrationTime=30
pirPin1 = storm.io.D2
pirPin2 = storm.io.D3
pirPin3 = storm.io.D4
shellip = "2001:470:66:3f9::2"
listen_port = 1337
sendsock = storm.net.udpsocket(listen_port, function() end)
lastval={0, 0, 0}
send = 1

function setup()
	storm.io.set_mode(storm.io.INPUT, pirPin1)
	storm.io.set_mode(storm.io.INPUT, pirPin2)
	storm.io.set_mode(storm.io.INPUT, pirPin3)
	storm.io.set(0, pirPin1)
	storm.io.set(0, pirPin2)
	storm.io.set(0, pirPin3)
	print("Calibrating sensor")
	for i=0, calibrationTime do
		cord.await(storm.os.invokeLater, storm.os.SECOND)
		print(".")
	end
	print("Done. Sensor ready")
	cord.await(storm.os.invokeLater, 50*storm.os.MILLISECOND)
end

function loop()
	pirVal1= storm.io.get(pirPin1)
	pirVal2= storm.io.get(pirPin2)
	pirVal3= storm.io.get(pirPin3)
	if(pirVal1 == 1) then print("Motion Detected 1")
    else print("Motion Not Detected 1") end

    if(pirVal2 == 1) then print("Motion Detected 2")
    else print("Motion Not Detected 2") end

    if(pirVal3 == 1) then print("Motion Detected 3")
    else print("Motion Not Detected 3") end
	return {pirVal1, pirVal2, pirVal3}
end 

cord.new(function()
	setup()
	while (1) do
		cord.await(storm.os.invokeLater, storm.os.SECOND)
		pirVals = loop()
		if(pirVals[1] ~= lastval[1]) then
		    data = {1, pirVals[1]}
            storm.net.sendto(sendsock, storm.mp.pack(data), shellip, 3000)
		    lastval[1]= pirVals[1]
        elseif(pirVals[2] ~= lastval[2]) then
		    data = {2, pirVals[2]}
            storm.net.sendto(sendsock, storm.mp.pack(data), shellip, 3001)
		    lastval[2]= pirVals[2]
        elseif(pirVals[3] ~= lastval[3]) then
		    data = {3, pirVals[3]}
            storm.net.sendto(sendsock, storm.mp.pack(data), shellip, 3002)
		    lastval[3]= pirVals[3]
		end

	end
	end
) --end of cord.new function

cord.enter_loop()

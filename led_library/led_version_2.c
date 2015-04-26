#define MAX 49 // addresses 3 at a time

#define START 0
#define HEADER 1
#define DATA 2
#define DONE 3

#define LED_SYMBOLS \
	{ LSTRKEY("led_init"), LFUNCVAL(led_init)}, \
	{ LSTRKEY("display"), LFUNCVAL(display)}, \
        { LSTRKEY("show"), LFUNCVAL(show)}, \
        { LSTRKEY("doSwapBuffersAsap"), LFUNCVAL(doSwapBuffersAsap)}, \
	{ LSTRKEY("set"), LFUNCVAL(set)}, \



unsigned int cc;

static uint16_t swapAsap = 0; 
static int lastdata = 0;
static int  blankCounter;
static int  bitCount;   // Used in interrupt
static uint16_t  ledIndex;
static int sendMode;
static struct led_strip led;

int display(lua_State *L);
int set(lua_State *L);

struct led_strip
{
 int nled;
 uint16_t * rgbpixel;
 int dpin;
 int cpin;
};

static const LUA_REG_TYPE led_meta_map[] =
{
 { LSTRKEY("set"), LFUNCVAL (set)},
 { LSTRKEY( "__index"), LROVAL ( led_meta_map)},
 {LNILKEY, LNILVAL},
};


/*void LPD6803::begin(void) {
  pinMode(dataPin, OUTPUT);
  pinMode(clockPin, OUTPUT);

  setCPUmax(cpumax);

  Timer1.attachInterrupt(LedOut);  // attaches callback() as a timer overflow interrupt
}*/

int led_init(lua_State *L)
{
 printf("Digital LED Strip Test\n");

 led.nled = (int)malloc(sizeof(int));
 int temp = lua_tonumber(L, 1);
 memcpy(&(led.nled), &temp, sizeof(int));
 
 led.rgbpixel = (uint16_t *)malloc(temp*sizeof(uint16_t));
 memset(led.rgbpixel, 0, temp*sizeof(uint16_t)); 

 temp = lua_tonumber(L,2);
 memcpy(&(led.dpin), &temp, sizeof(int));
 
 temp = lua_tonumber(L,3);
 memcpy(&(led.cpin), &temp, sizeof(int));
  
 //set them as output pins
 lua_pushlightfunction(L, libstorm_io_set_mode);
 lua_pushnumber(L,0);
 lua_pushnumber(L, led.dpin); //D4
 lua_pushnumber(L, led.cpin); //D5
 lua_call(L, 3, 0);

  sendMode = START;
  blankCounter = 0;
  bitCount = 0;
  ledIndex = 0;

 lua_pushlightfunction(L, libstorm_os_invoke_periodically);
 lua_pushnumber(L, 1*MILLISECOND_TICKS);
 lua_pushlightfunction(L, display);
 lua_call(L, 2, 0);
 return 1;
}

int display(lua_State *L) {
   printf("LED Strip Display Test\n");
   switch(sendMode) {
    case DONE:            //Done..just send clocks with zero data
      if (swapAsap>0) {
        if(!blankCounter)    //AS SOON AS CURRENT pwm IS DONE. BlankCounter 
      	{
        	bitCount = 0;
        	ledIndex = swapAsap;  //set current led
        	sendMode = HEADER;
	      	swapAsap = 0;
      	}   	
      }
      break;

    case DATA:               //Sending Data
      if ((1 << (15-bitCount)) & led.rgbpixel[ledIndex]) {
		if (!lastdata) {     // digitalwrites take a long time, avoid if possible
	  		// If not the first bit then output the next bits 
	  		// (Starting with MSB bit 15 down.)
	  		//digitalWrite(dataPin, 1);
			lua_pushlightfunction(L, libstorm_io_set);
			lua_pushnumber(L,1);
			lua_pushnumber(L, led.dpin);
			lua_call(L, 2, 0);
	  		lastdata = 1;
		}
      } else {
		if (lastdata) {       // digitalwrites take a long time, avoid if possible
	  		//digitalWrite(dataPin, 0);
			lua_pushlightfunction(L, libstorm_io_set);
			lua_pushnumber(L,0);
			lua_pushnumber(L, led.dpin);
			lua_call(L, 2, 0);
	  		lastdata = 0;
		}
      }
      bitCount++;
      
      if(bitCount == 16)    //Last bit?
      {
        ledIndex++;        //Move to next LED
        if (ledIndex < led.nled) //Still more leds to go or are we done?
        {
          bitCount=0;      //Start from the fist bit of the next LED
        } else {
	  		// no longer sending data, set the data pin low
	  		//digitalWrite(dataPin, 0);
			lua_pushlightfunction(L, libstorm_io_set);
			lua_pushnumber(L,0);
			lua_pushnumber(L, led.dpin);
			lua_call(L, 2, 0);
	  		lastdata = 0; // this is a lite optimization
          	sendMode = DONE;  //No more LEDs to go, we are done!
		}
      }
      break;      
    case HEADER:            //Header
      if (bitCount < 32) {
		//digitalWrite(dataPin, 0);
     		lua_pushlightfunction(L, libstorm_io_set);
		lua_pushnumber(L,0);
		lua_pushnumber(L, led.dpin);
		lua_call(L, 2, 0);
		lastdata = 0;
		bitCount++;
		if (bitCount==32) {
	  		sendMode = DATA;      //If this was the last bit of header then move on to data.
	  		ledIndex = 0;
	  		bitCount = 0;
		}
      }
      break;
    case START:            //Start
      if (!blankCounter)    //AS SOON AS CURRENT pwm IS DONE. BlankCounter 
      {
        bitCount = 0;
        ledIndex = 0;
        sendMode = HEADER; 
      }  
      break;   
  }

  // Clock out data (or clock LEDs)
  //digitalWrite(clockPin, HIGH);
  lua_pushlightfunction(L, libstorm_io_set);
  lua_pushnumber(L,1);
  lua_pushnumber(L, led.cpin);
  lua_call(L, 2, 0);

  //digitalWrite(clockPin, LOW);
  lua_pushlightfunction(L, libstorm_io_set);
  lua_pushnumber(L,0);
  lua_pushnumber(L, led.cpin);
  lua_call(L, 2, 0);
  
  //Keep track of where the LEDs are at in their pwm cycle. 
  blankCounter++;
}

/*
int display(lua_State *L)
{
    printf("LED Strip Display Test\n");
    struct led_strip *led = lua_touserdata(L,1);

    //Set data pin to low
    lua_pushlightfunction(L, libstorm_io_set);
	lua_pushnumber(L,0);
	lua_pushnumber(L, led.dpin);
	lua_call(L, 2, 0);
    //Toggle clock pin 32 times
    int k;
    for (k=0; k<32; k++) {
        lua_pushlightfunction(L, libstorm_io_set);
		lua_pushnumber(L,1);
		lua_pushnumber(L, led.cpin);
		lua_call(L, 2, 0);
 		lua_pushlightfunction(L, libstorm_io_set);
		lua_pushnumber(L,0);
		lua_pushnumber(L, led.cpin);
		lua_call(L, 2, 0);
    }
    
    // Iterate over all leds
    int i,j;
    for(i=0;i<led.nled;i++)
    {
        //Output 1 as start bit
        lua_pushlightfunction(L, libstorm_io_set);
        lua_pushnumber(L,1);
        lua_pushnumber(L, led.dpin);
        lua_call(L, 2, 0);
 		lua_pushlightfunction(L, libstorm_io_set);
		lua_pushnumber(L,1);
		lua_pushnumber(L, led.cpin);
		lua_call(L, 2, 0);
 		lua_pushlightfunction(L, libstorm_io_set);
		lua_pushnumber(L,0);
		lua_pushnumber(L, led.cpin);
		lua_call(L, 2, 0);

        uint16_t this_color= led.rgbpixel[i];
        printf("%x\n", led.rgbpixel[i]);
        for(j=14; j>=0; j--)
        {	
    		uint16_t mask = 1<< j;
    		if(this_color & mask)
    		{
     			lua_pushlightfunction(L, libstorm_io_set);
    			lua_pushnumber(L,1);
    			lua_pushnumber(L, led.dpin);
    			lua_call(L, 2, 0);
                //printf("index %d write high", i);
    		}
	        else
	    	{
 	    		lua_pushlightfunction(L, libstorm_io_set);
	    		lua_pushnumber(L,0);
	    		lua_pushnumber(L, led.dpin);
	    		lua_call(L, 2, 0);
                //printf("index %d write low", j);
	    	}
			
 		    lua_pushlightfunction(L, libstorm_io_set);
		    lua_pushnumber(L,1);
		    lua_pushnumber(L, led.cpin);
		    lua_call(L, 2, 0);
 		    lua_pushlightfunction(L, libstorm_io_set);
		    lua_pushnumber(L,0);
		    lua_pushnumber(L, led.cpin);
		    lua_call(L, 2, 0);
	    }
        lua_pushlightfunction(L, libstorm_os_invoke_later);
        lua_pushnumber(L, 0.5 * MILLISECOND_TICKS);
    }
    //nled pulse
 	lua_pushlightfunction(L, libstorm_io_set);
	lua_pushnumber(L,0);
	lua_pushnumber(L, led.dpin);
	lua_call(L, 2, 0);
    int l;
    for (l=0; l<8*led.nled; l++) {
 		lua_pushlightfunction(L, libstorm_io_set);
		lua_pushnumber(L,1);
		lua_pushnumber(L, led.cpin);
		lua_call(L, 2, 0);
 		lua_pushlightfunction(L, libstorm_io_set);
		lua_pushnumber(L,0);
		lua_pushnumber(L, led.cpin);
		lua_call(L, 2, 0);
    }

    lua_pushlightfunction(L, libstorm_os_invoke_later);
    lua_pushnumber(L, 1 * MILLISECOND_TICKS);
    return 0;
}*/


int set(lua_State *L)
{
    printf("LED Strip Set Test\n");
	//struct led_strip *led = lua_touserdata(L,1);
	int ind = lua_tonumber(L, 2);
	uint16_t r = (uint16_t)lua_tonumber(L,3); 
	uint16_t g = (uint16_t)lua_tonumber(L,4); 
	uint16_t b = (uint16_t)lua_tonumber(L,5); 

	if( (r>31) || (g>31) || (b>31))
	{
		printf("RGB values out of range\n");
		return 0;
	}
    uint16_t data;
    data = g & 0x1F;
    data <<= 5;
    data |= b & 0x1F;
    data <<= 5;
    data |= r & 0x1F;
    data |= 0x8000;
    printf("%x\n", data);
	led.rgbpixel[ind] = data;
    //printf("%d", led.rgbpixel[index]);
	return 0;
}

int doSwapBuffersAsap(lua_State *L) {
  int idx = lua_tonumber(L,1);
  swapAsap = idx;
  return 0;
}

int show(lua_State *L) {
  sendMode = START;
  return 0;
}
 

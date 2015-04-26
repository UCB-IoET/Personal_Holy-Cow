#define MAX 49 // addresses 3 at a time

#define LED_SYMBOLS \
	{ LSTRKEY("led_init"), LFUNCVAL(led_init)}, \
	{ LSTRKEY("lua_display"), LFUNCVAL(display)}, \


unsigned int cc;

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
 { LSTRKEY("display"), LFUNCVAL (display)},
 { LSTRKEY("set"), LFUNCVAL (set)},
 { LSTRKEY( "__index"), LROVAL ( led_meta_map)},
 {LNILKEY, LNILVAL},
};

static int dummy(lua_State *L){
	printf("HELLO\n");
	return 0;
}

int led_init(lua_State *L)
{
 printf("Digital LED Strip Test\n");
 struct led_strip * led = lua_newuserdata(L, sizeof(struct led_strip));  

 led->nled = (int)malloc(sizeof(int));
 int temp = lua_tonumber(L, 1);
 memcpy(&(led->nled), &temp, sizeof(int));
 
 led->rgbpixel = (uint16_t *)malloc(temp*sizeof(uint16_t));
 memset(led->rgbpixel, 0, temp*sizeof(uint16_t)); 

 temp = lua_tonumber(L,2);
 memcpy(&(led->dpin), &temp, sizeof(int));
 
 temp = lua_tonumber(L,3);
 memcpy(&(led->cpin), &temp, sizeof(int));
  
 //set them as output pins
 lua_pushlightfunction(L, libstorm_io_set_mode);
 lua_pushnumber(L,0);
 lua_pushnumber(L, led->dpin); //D4
 lua_pushnumber(L, led->cpin); //D5
 lua_call(L, 3, 0);

 lua_pushrotable (L, (void *) led_meta_map);
 lua_setmetatable(L, -2);
 return 1;
}


/*

http://interface.khm.de/index.php/lab-log/digital-addressable-led-strip-arduino/

void show() {
  unsigned int ii,b1;
  for (ii=0; ii < nled; ii++ ) {

    bitWrite(PORTD,datapin,HIGH);
    bitWrite(PORTD,clockpin, HIGH);
    bitWrite(PORTD,clockpin, LOW);

    for ( b1=0x4000; b1; b1 >>= 1) {

      if(rgbPixel[ii] & b1) bitWrite(PORTD,datapin, HIGH);
      else                bitWrite(PORTD,datapin, LOW);
      bitWrite(PORTD,clockpin, HIGH);
      bitWrite(PORTD,clockpin, LOW);
    }
  }
  latchLeds(nled);
}
//*********************************************************
// activate new color pattern in ledstrip
void latchLeds(int n) {

  bitWrite(PORTD,datapin, LOW);
  for(int i = 8 * n; i>0; i--) {
    bitWrite(PORTD,clockpin, HIGH);
    bitWrite(PORTD,clockpin, LOW);
  }

}*/

int display(lua_State *L) {
	printf("LED Strip Display\n");
	 struct led_strip *led = lua_touserdata(L,1);
	int nled = lua_tonumber(L, 2);
	int ii;
	for (ii = 0; ii < nled; ii++) {
		//bitWrite(PORTD,datapin,HIGH);
		lua_pushlightfunction(L, libstorm_io_set);
		lua_pushnumber(L,1);
		lua_pushnumber(L, led->dpin);
		lua_call(L, 2, 0);
		
    		//bitWrite(PORTD,clockpin, HIGH);
		lua_pushlightfunction(L, libstorm_io_set);
		lua_pushnumber(L,1);
		lua_pushnumber(L, led->cpin);
		lua_call(L, 2, 0);

		//bitWrite(PORTD,clockpin, LOW);
 		lua_pushlightfunction(L, libstorm_io_set);
		lua_pushnumber(L,0);
		lua_pushnumber(L, led->cpin);
		lua_call(L, 2, 0);
		
		unsigned int b1;
		for ( b1=0x4000; b1; b1 >>= 1) {
		
			/*if(rgbPixel[ii] & b1) bitWrite(PORTD,datapin, HIGH);
      			else                bitWrite(PORTD,datapin, LOW);
      			bitWrite(PORTD,clockpin, HIGH);
      			bitWrite(PORTD,clockpin, LOW);*/

			if (led->rgbpixel[ii] & b1) {
				lua_pushlightfunction(L, libstorm_io_set);
				lua_pushnumber(L,1);
				lua_pushnumber(L, led->dpin);
				lua_call(L, 2, 0);
			} else {
				lua_pushlightfunction(L, libstorm_io_set);
				lua_pushnumber(L,0);
				lua_pushnumber(L, led->dpin);
				lua_call(L, 2, 0);
			}
			    		//bitWrite(PORTD,clockpin, HIGH);
			lua_pushlightfunction(L, libstorm_io_set);
			lua_pushnumber(L,1);
			lua_pushnumber(L, led->cpin);
			lua_call(L, 2, 0);

			//bitWrite(PORTD,clockpin, LOW);
 			lua_pushlightfunction(L, libstorm_io_set);
			lua_pushnumber(L,0);
			lua_pushnumber(L, led->cpin);
			lua_call(L, 2, 0);

		}
	}
	/*bitWrite(PORTD,datapin, LOW);
  	for(int i = 8 * n; i>0; i--) {
    	bitWrite(PORTD,clockpin, HIGH);
    	bitWrite(PORTD,clockpin, LOW);*/
	
	lua_pushlightfunction(L, libstorm_io_set);
	lua_pushnumber(L,1);
	lua_pushnumber(L, led->dpin);
	lua_call(L, 2, 0);
	int i;
	for (i = (8 * nled); i >0 ; i--) {
		//bitWrite(PORTD,clockpin, HIGH);
		lua_pushlightfunction(L, libstorm_io_set);
		lua_pushnumber(L,1);
		lua_pushnumber(L, led->cpin);
		lua_call(L, 2, 0);

		//bitWrite(PORTD,clockpin, LOW);
 		lua_pushlightfunction(L, libstorm_io_set);
		lua_pushnumber(L,0);
		lua_pushnumber(L, led->cpin);
		lua_call(L, 2, 0);
	}
}

/*
int display(lua_State *L)
{
    printf("LED Strip Display Test\n");
    struct led_strip *led = lua_touserdata(L,1);

    //Set data pin to low
    lua_pushlightfunction(L, libstorm_io_set);
	lua_pushnumber(L,0);
	lua_pushnumber(L, led->dpin);
	lua_call(L, 2, 0);
    //Toggle clock pin 32 times
    int k;
    for (k=0; k<32; k++) {
        lua_pushlightfunction(L, libstorm_io_set);
		lua_pushnumber(L,1);
		lua_pushnumber(L, led->cpin);
		lua_call(L, 2, 0);
 		lua_pushlightfunction(L, libstorm_io_set);
		lua_pushnumber(L,0);
		lua_pushnumber(L, led->cpin);
		lua_call(L, 2, 0);
    }
    
    // Iterate over all leds
    int i,j;
    for(i=0;i<led->nled;i++)
    {
        //Output 1 as start bit
        lua_pushlightfunction(L, libstorm_io_set);
        lua_pushnumber(L,1);
        lua_pushnumber(L, led->dpin);
        lua_call(L, 2, 0);
 		lua_pushlightfunction(L, libstorm_io_set);
		lua_pushnumber(L,1);
		lua_pushnumber(L, led->cpin);
		lua_call(L, 2, 0);
 		lua_pushlightfunction(L, libstorm_io_set);
		lua_pushnumber(L,0);
		lua_pushnumber(L, led->cpin);
		lua_call(L, 2, 0);

        uint16_t this_color= led->rgbpixel[i];
        printf("%x\n", led->rgbpixel[i]);
        for(j=14; j>=0; j--)
        {	
    		uint16_t mask = 1<< j;
    		if(this_color & mask)
    		{
     			lua_pushlightfunction(L, libstorm_io_set);
    			lua_pushnumber(L,1);
    			lua_pushnumber(L, led->dpin);
    			lua_call(L, 2, 0);
                //printf("index %d write high", i);
    		}
	        else
	    	{
 	    		lua_pushlightfunction(L, libstorm_io_set);
	    		lua_pushnumber(L,0);
	    		lua_pushnumber(L, led->dpin);
	    		lua_call(L, 2, 0);
                //printf("index %d write low", j);
	    	}
			
 		    lua_pushlightfunction(L, libstorm_io_set);
		    lua_pushnumber(L,1);
		    lua_pushnumber(L, led->cpin);
		    lua_call(L, 2, 0);
 		    lua_pushlightfunction(L, libstorm_io_set);
		    lua_pushnumber(L,0);
		    lua_pushnumber(L, led->cpin);
		    lua_call(L, 2, 0);
	    }
        lua_pushlightfunction(L, libstorm_os_invoke_later);
        lua_pushnumber(L, 0.5 * MILLISECOND_TICKS);
    }
    //nled pulse
 	lua_pushlightfunction(L, libstorm_io_set);
	lua_pushnumber(L,0);
	lua_pushnumber(L, led->dpin);
	lua_call(L, 2, 0);
    int l;
    for (l=0; l<8*led->nled; l++) {
 		lua_pushlightfunction(L, libstorm_io_set);
		lua_pushnumber(L,1);
		lua_pushnumber(L, led->cpin);
		lua_call(L, 2, 0);
 		lua_pushlightfunction(L, libstorm_io_set);
		lua_pushnumber(L,0);
		lua_pushnumber(L, led->cpin);
		lua_call(L, 2, 0);
    }

    lua_pushlightfunction(L, libstorm_os_invoke_later);
    lua_pushnumber(L, 1 * MILLISECOND_TICKS);
    return 0;
}*/


int set(lua_State *L)
{
    printf("LED Strip Set Test\n");
	struct led_strip *led = lua_touserdata(L,1);
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
	led->rgbpixel[ind] = data;
    //printf("%d", led->rgbpixel[index]);
	return 0;
}
 

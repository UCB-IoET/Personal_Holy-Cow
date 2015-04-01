#define LED_SYMBOLS \
	{ LSTRKEY("led_init"), LFUNCVAL(led_init)}, \


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
 lua_pushnumber(L, led->dpin);
 lua_pushnumber(L, led->cpin);
 lua_call(L, 3, 0);

 lua_pushrotable (L, (void *) led_meta_map);
 lua_setmetatable(L, -2);
 return 1;
}

/*
int display(lua_State *L)
{
    uint32_t z;
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
        for(j=0x4000; j; j >>= 1)
        {	
    		if(this_color & j)
    		{
     			lua_pushlightfunction(L, libstorm_io_set);
    			lua_pushnumber(L,1);
    			lua_pushnumber(L, led->dpin);
    			lua_call(L, 2, 0);
                printf("index %d write high", i);
    		}
	        else
	    	{
 	    		lua_pushlightfunction(L, libstorm_io_set);
	    		lua_pushnumber(L,0);
	    		lua_pushnumber(L, led->dpin);
	    		lua_call(L, 2, 0);
                printf("index %d write low", j);
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

    return 0;
}
*/
/*
int display(lua_State *L)
{
    printf("LED Strip Display Test\n");
    struct led_strip *led = lua_touserdata(L,1);
	uint32_t volatile *reg_gpio = (uint32_t *)0x400E1004;
	*reg_gpio = 1 << 16 | 1 << 12;
	uint32_t volatile *reg_oder = (uint32_t *)0x400E1044;
	*reg_oder = 1 << 16 | 1 << 12;
	uint32_t volatile *reg_ovrs = (uint32_t *)0x400E1054;
    *reg_ovrs = 0;
    uint32_t volatile *reg_ovrc = (uint32_t *)0x400E1058;
    *reg_ovrc = 0;

    //Set data pin to low
    *reg_ovrc = 1 << 16;
    loop();
    //Toggle clock pin 32 times
    int k;
    for (k=0; k<32; k++) {
        *reg_ovrs = 1 << 12;
        loop();
        *reg_ovrc = 1 << 12;
        loop();
    }
    
    // Iterate over all leds
    int i,j;
    for(i=0;i<led->nled;i++)
    {
        //Output 1 as start bit
        *reg_ovrs = 1 << 16;
        loop();
        *reg_ovrs = 1 << 12;
        loop();
        *reg_ovrc = 1 << 12;
        loop();

        uint16_t this_color= led->rgbpixel[i];
        //printf("%x\n", led->rgbpixel[i]);
        for(j=0x4000; j; j >>= 1)
        {	
    		if(this_color & j)
    		{
                *reg_ovrs = 1 << 16;
                loop();
    		}
	        else
	    	{
                *reg_ovrc = 1 << 16;
                loop();
	    	}
            *reg_ovrs = 1 << 12;
            loop();
            *reg_ovrc = 1 << 12;
            loop();
	    }
      
    }
    //nled pulse
    *reg_ovrc = 1 << 16;
    loop();
    int l;
    for (l=0; l<8*led->nled; l++) {
        *reg_ovrs = 1 << 12;
        loop();
        *reg_ovrc = 1 << 12;
        loop();
    }

    return 0;
}
*/
int display(lua_State *L)
{
    printf("LED Strip Display Test\n");
    struct led_strip *led = lua_touserdata(L,1);
	uint32_t volatile *reg_gpio = (uint32_t *)0x400E1004;
	*reg_gpio = 1 << 16 | 1 << 12;
	uint32_t volatile *reg_oder = (uint32_t *)0x400E1044;
	*reg_oder = 1 << 16 | 1 << 12;
	uint32_t volatile *reg_ovrs = (uint32_t *)0x400E1054;
    uint32_t volatile *reg_ovrc = (uint32_t *)0x400E1058;

    //Set data pin to low
    *reg_ovrc = 1 << 16;
    loop();
    //Toggle clock pin 32 times
    int k;
    for (k=0; k<32; k++) {
        *reg_ovrs = 1 << 12;
        loop();
        *reg_ovrc = 1 << 12;
        loop();
    }
    
    // Iterate over all leds
    int i,j;
    for(i=0;i<led->nled;i++)
    {
        //Output 1 as start bit
        *reg_ovrs = 1 << 16;
        loop();
        *reg_ovrs = 1 << 12;
        loop();
        *reg_ovrc = 1 << 12;
        loop();

        uint16_t this_color= led->rgbpixel[i];
        char dr = ((this_color>>10) & 0x1f); // red data   (0 - 31)
        char dg = ((this_color>>5) & 0x1f); // green data (0 - 31)
        char db = (this_color & 0x1f);
        //printf("%x\n", led->rgbpixel[i]);
        char mask = 0x10;
        for (j = 0; j < 5; j++) {
            if (mask & dr) {
                *reg_ovrs = 1 << 16;
                loop();
    		}
            else {
                *reg_ovrc = 1 << 16;
                loop();
            }
            *reg_ovrs = 1 << 12;
            loop();
            *reg_ovrc = 1 << 12;
            loop();
            mask >>= 1;
        }
        mask = 0x10;
        for (j = 0; j < 5; j++) {
            if (mask & dg) {
                *reg_ovrs = 1 << 16;
                loop();
    		}
            else {
                *reg_ovrc = 1 << 16;
                loop();
            }
            *reg_ovrs = 1 << 12;
            loop();
            *reg_ovrc = 1 << 12;
            loop();
            mask >>= 1;
        }

        mask = 0x10;
        for (j = 0; j < 5; j++) {
            if (mask & db) {
                *reg_ovrs = 1 << 16;
                loop();
    		}
            else {
                *reg_ovrc = 1 << 16;
                loop();
            }
            *reg_ovrs = 1 << 12;
            loop();
            *reg_ovrc = 1 << 12;
            loop();
            mask >>= 1;
        }
    }
        
    //nled pulse
    *reg_ovrc = 1 << 16;
    loop();
    int l;
    for (l=0; l<led->nled; l++) {
        *reg_ovrs = 1 << 12;
        loop();
        *reg_ovrc = 1 << 12;
        loop();
    }
    printf("end");
    return 0;
}

void loop() {
    int i;
    for(i = 0; i < 56; i++);
}

int set(lua_State *L)
{
    printf("LED Strip Set Test\n");
	struct led_strip *led = lua_touserdata(L,1);
	int index = lua_tonumber(L, 2);
	uint16_t r = (uint16_t)lua_tonumber(L,3); 
	uint16_t g = (uint16_t)lua_tonumber(L,4); 
	uint16_t b = (uint16_t)lua_tonumber(L,5); 

	if( (r>31) || (g>31) || (b>31))
	{
		printf("RGB values out of range\n");
		return 0;
	}
    r=r & 0x1F;
    g=g & 0x1F;
    b=b & 0x1F;
    uint16_t data = (b << 10) | (r << 5) | g;
    printf("%x\n", data);
	led->rgbpixel[index] = data;
    //printf("%d", led->rgbpixel[index]);
	return 0;
}
 

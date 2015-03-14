#define MAX 49 // addresses 3 at a time

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

void toggle_clock(int cpin)
{

	led_set(1, cpin);
	led_set(0, cpin);
}

void led_set(int value, int pin)
{
	lua_pushlightfunction(L, storm_io_set);
        lua_pushnumber(value);
	lua_pushnumber(pin);
	lua_call(L, 2, 0);
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

int display(lua_State *L)
{
 printf("LED Strip Display Test\n");
 struct led_strip *led = lua_touserdata(L,1);
 toggle_clock();
 int k;
 for (k=0; k<31; k++) {
		led_set(0, led->dpin);
		toggle_clock();

}
 int i,j;
 for(i=0;i<led->nled;i++)
 {
	led_set(1, led->dpin);
	toggle_clock();
	uint16_t this_color= led->rgbpixel[i];
	printf("%x\n", led->rgbpixel[i]);
	for(j=14; j>=0; j--)
	{	
		uint16_t mask = 1<< j;
		if(this_color & mask)
		{
			led_set(1, led->dpin);
            printf("index %d write high", i);
		}

		else
		{
			led_set(0, led->dpin);
            //printf("index %d write low", j);
		}
		
 	toggle_clock();	
	}
 }
 
 toggle_clock();
 led_det(0, led->dpin);
 toggle_clock();
/*
int k;
for(k = 8 * led->nled; k>0; k--) {
 lua_pushlightfunction(L, libstorm_io_set);
 lua_pushnumber(L,1);
 lua_pushnumber(L, led->cpin);
 lua_call(L, 2, 0);
 lua_pushlightfunction(L, libstorm_io_set);
 lua_pushnumber(L,0);
 lua_pushnumber(L, led->cpin);
 lua_call(L, 2, 0);
  }*/


 
 return 0;

}


int set(lua_State *L)
{
    printf("LED Strip Set Test\n");
	struct led_strip *led = lua_touserdata(L,1);
	int index = lua_tonumber(L, 2);
	uint32_t r = (uint32_t)lua_tonumber(L,3); 
	uint32_t g = (uint32_t)lua_tonumber(L,4); 
	uint32_t b = (uint32_t)lua_tonumber(L,5); 

	if( (r>255) || (g>255) || (b>255))
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
	led->rgbpixel[index] = data;
    //printf("%d", led->rgbpixel[index]);
	return 0;
}
 

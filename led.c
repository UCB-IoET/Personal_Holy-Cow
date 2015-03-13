#define MAX 49 // addresses 3 at a time

#define LED_SYMBOLS \
	{ LSTRKEY("led_init"), LFUNCVAL(led_init)}, \

unsigned int cc;

struct led_strip
{
 int nled;
 unsigned int rgbpixel[MAX];
 int dpin;
 int cpin;
};

struct const LUA_REG_TYPE led_meta_map[] =
{
 { LSTRKEY("display"), LFUNCVAL (led_display)},
 {LNILKEY, LNILVAL}
};


int led_init(lua_State *L)
{
 printf("Digital LED Strip Test\n");
 struct led_strip led = lua_newuserdata(L, sizeof(struct led_strip));  

 led->nled = (int)malloc(sizeof(int));
 int temp = lua_tonumber(L, 1);
 memcpy(&(led->nled), &temp, sizeof(int));
 
 led->rgbpixel = (int *)malloc(temp*sizeof(unsigned int));
 memset(led->rgbpixel, 0, temp);
 
 temp = lua_tonumber(L,2);
 memcpy(&(led->dpin), &temp, sizeof(int));
 
 temp = lua_tonumber(L,3);
 memcpy(&(led->cpin), &temp, sizeof(int));
  
 //storm.io.set(1, storm.io.D4, storm.io.D5);
 //set them as output pins

 lua_pushlightfunction(L, storm.io.set);
 lua_pushnumber(L,0);
 lua_pushnumber(L, led->dpin); //D4
 lua_pushnumber(L, led->cpin); //D5
 lua_call(L, 4, 0);
 
 lua_pushrotable (L, (void *) led_meta_map);
 lua_setmetatable(L, -2);
 return 1;
}

int display(lua_State *L)
{
 struct led_strip *led = lua_touserdata(L,1);
 
 int i,j;
 for(i=0;i<led->nled;i++)
 {
	uint32_t this_color= rgbpixel[i];
	
	for(j=23; j>=0; j--)
	{
		//write LOW to clock
 		lua_pushlightfunction(L, storm.io.set);
		lua_pushnumber(L,0);
		lua_pushnumber(L, led->cpin);
		lua_call(L, 2, 0);
		
		uint32_t mask = 1<< 24;
		if(this_color & mask)
		{
 			lua_pushlightfunction(L, storm.io.set);
			lua_pushnumber(L,1);
			lua_pushnumber(L, led->dpin);
			lua_call(L, 2, 0);
		}

		else
		{
 			lua_pushlightfunction(L, storm.io.set);
			lua_pushnumber(L,1);
			lua_pushnumber(L, led->dpin);
			lua_call(L, 2, 0);
		}
		
		
 		lua_pushlightfunction(L, storm.io.set);
		lua_pushnumber(L,1);
		lua_pushnumber(L, led->cpin);
		lua_call(L, 2, 0);
	}
 }

 lua_pushlightfunction(L, storm.io.set);
 lua_pushnumber(L,0);
 lua_pushnumber(L, led->cpin);
 lua_call(L, 2, 0);
 
 return 0;

}


int set(lua_State *L)
{
	struct led_strip *led = lua_touserdata(L,1);
	int index = lua_tonumber(L, 2);
	uint32_t r = (uint32_t)lua_tonumber(L,3); 
	uint32_t g = (uint32_t)lua_tonumber(L,3); 
	uint32_t b = (uint32_t)lua_tonumber(L,3); 

	if( (r>255) || (g>255) || (b>255))
	{
		printf("RGB values out of range\n");
		return 0;
	}

	led->rgbpixel[index] = ((r<<4) | (g<<2) | b;
	return 0;
}
 

#ifndef Display_h
#define Display_h

#include <LedControl.h>

#if (ARDUINO >= 100)
#include <Arduino.h>
#else
#include <WProgram.h>
#endif

class Bargraph {
  public :
    String name;
	String api;
	
	Bargraph(String _name, String _api, String _max, int _device);
	Bargraph(String _name, String _api, String _max, int _device, String _type);
	
	void set(long _value);
	void update();
    void print();
  
  private :
	 long max;
	 long value;
	 int device;
	 int size;
	 String type;
	 
	 
	 void format();
	 void write();
};

#endif
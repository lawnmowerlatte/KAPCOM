#ifndef Bargraph_h
#define Bargraph_h

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_LEDBackpack.h>

#if (ARDUINO >= 100)
#include <Arduino.h>
#else
#include <WProgram.h>
#endif

class Bargraph {
  public :
    String name;
	String api;
	Adafruit_24bargraph bar;
	
	Bargraph(String _name, String _api, int _device,
		String _type="Default");
	
	void set(String _value);
	void setMax(String _max);
	void update();
    void print();
  
  private :
  	
	int display[24];
  
	long max;
	long value;
	int device;
	int size;
	String type;
	 
	void format();
	void write();
};

#endif
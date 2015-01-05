#ifndef Display_h
#define Display_h

#include <LedControl.h>

#if (ARDUINO >= 100)
#include <Arduino.h>
#else
#include <WProgram.h>
#endif

class Display {
  public :
    String name;
	String api;
	
	void set(long _value);
	void update();
    void print();
  
  private :
 	 LedControl l;
	 long value;
	 String formatted;
	 int device;
	 int length;
	 int offset;
	 
	 void format();
	 void write();
};

#endif
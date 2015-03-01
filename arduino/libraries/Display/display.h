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
	
	Display(String _name, String _api, LedControl _l, int _length, int _device, 
		int _offset=0,
		int _decimals=2,
		String _pad=" ");
	
	void set(String _value);
	void update();
    void print();
  
  private :
 	 LedControl l;
	 String value;
	 String formatted;
	 String pad;
	 int device;
	 int length;
	 int offset;
	 int decimals;
	 
	 void format();
	 void write();
};

#endif
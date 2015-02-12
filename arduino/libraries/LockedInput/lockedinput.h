#ifndef LockedInput_h
#define LockedInput_h

#include <pin.h>

#if (ARDUINO >= 100)
#include <Arduino.h>
#else
#include <WProgram.h>
#endif

class LockedInput {
  public :
    String name;
	String api;
	int value;
  	Pin lock;
	Pin button;
	Pin indicator;
    
    LockedInput(String _name, String _api, int _lock, int _button, int _indicator,
		String _format="Value");
	
	int get();
	String toString();
    void update();
	bool changed();
    void print();
	
  private :
	int last_value;
	String format;
};

#endif
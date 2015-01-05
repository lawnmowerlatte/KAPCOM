#ifndef LockedInput_h
#define LockedInput_h

#include <pin.h>
#include <pinio.h>

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
    
    LockedInput(String _name, String _api, int _lock, int _button, int _indicator);
    
	int get();
    void update();
	bool updated();
    void print();
	
  private :
	int last_value;
};

#endif
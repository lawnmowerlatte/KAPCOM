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
    PinIO lock;
    PinIO button;
    
    LockedInput(String _name, String _api, int _lock_in, int _lock_out, int _button_in, int _button_out);
    
    void update();
    void print();
};

#endif
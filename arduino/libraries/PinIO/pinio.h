#ifndef PinIO_h
#define PinIO_h

#include <pin.h>

#if (ARDUINO >= 100)
#include <Arduino.h>
#else
#include <WProgram.h>
#endif

class PinIO {
  public :
    String name;
	String api;
    Pin in;
    Pin out;
    
    PinIO(String _name, String _api, int _in, int _out);
    
    void update();
    void print();
};

#endif
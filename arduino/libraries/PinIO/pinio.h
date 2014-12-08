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
    Pin in;
    Pin out;
    
    PinIO(String _name, int _in, int _out);
    
    void update();
    void print();
};

#endif
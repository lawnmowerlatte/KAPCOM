#ifndef Joy_h
#define Joy_h

#include <pin.h>

#if (ARDUINO >= 100)
#include <Arduino.h>
#else
#include <WProgram.h>
#endif

class Joy {
  public :
    String name;
    Pin x;
    Pin y;
    Pin z;
    int X;
    int Y;
    int Z;
    
    Joy(String _name, int _x, int _y, int _z);
    Joy(String _name, int _x, int _y, int _z, int _min, int _max);
    
    void update();
    void print();
  
  private :
    int min;
    int max;
    int scale;
};

#endif
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
	Pin button;
    float X;
    float Y;
    float Z;
    
    Joy(String _name, int _x, int _y, int _z, int _button,
		bool _invertX=false,
		bool _invertY=false,
		bool _invertZ=false,
		int _min=0,
		int _max=1023);
    
	void update();
	bool centered();
    void print();
	String toString();
  
  private :
	bool center;
    int scale;
};

#endif
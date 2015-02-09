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
	bool invertX;
	bool invertY;
	bool invertZ;
    
    Joy(String _name, int _x, int _y, int _z, int _button);
	Joy(String _name, int _x, int _y, int _z, int _button, bool _invertX, bool _invertY, bool _invertZ);
    Joy(String _name, int _x, int _y, int _z, int _button, int _min, int _max);
    
	void invertAxis(String axis);
	void recalibrate();
	void calibrate();
    void update();
	bool centered();
    void print();
	String toString();
  
  private :
	bool center;
    int min;
	int xMin;
	int yMin;
	int zMin;
    int max;
	int xMax;
	int yMax;
	int zMax;
    int scale;
};

#endif
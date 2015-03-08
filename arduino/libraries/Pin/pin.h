#ifndef Pin_h
#define Pin_h

#if (ARDUINO >= 100)
#include <Arduino.h>
#else
#include <WProgram.h>
#endif

class Pin {
  public :
    String name;
	String api;
    int value;
	float fvalue;
	bool invert;
  
    Pin(String _name, String _api, int _pin, boolean _type, boolean _mode, 
		String _format="Value",
		int _cooldown=500,
		int _min=0,
		int _max=1023,
		int _invert=false);
    
    int get();
	float getFloat();
	void set(int _value);
	void set(String _value);
    void update();
	bool changed();
	String toString();
    void print();
  
  private :
    int pin;
    boolean type;
    boolean mode;
    int last_update;
	int last_value;
    int cooldown;
	String format;
	int min;
	int max;
    
    void read();
    void write();
};

#endif
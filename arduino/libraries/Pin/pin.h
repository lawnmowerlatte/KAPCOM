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
  
    Pin(String _name, String _api, int _pin, boolean _type, boolean _mode);
    Pin(String _name, String _api, int _pin, boolean _type, boolean _mode, int _cooldown);
    
    int get();
    void set(int _value);
	bool updated();
    void update();
    void print();
  
  private :
    int pin;
    boolean type;
    boolean mode;
    int last_update;
	int last_value;
    int cooldown;
    
    void read();
    void write();
    
};

#endif
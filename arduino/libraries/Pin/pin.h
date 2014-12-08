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
    int pin;
    boolean type;
    boolean mode;
    int state;
    int value;
  
    Pin(String _name, int _pin, boolean _type, boolean _mode);
    Pin(String _name, int _pin, boolean _type, boolean _mode, int _cooldown);
    
    int get();
    void set(boolean _state);
    void set(int _state);
    void update();
    void print();
  
  private :
    int updated;
    int cooldown;
    
    void read();
    void write();
    
};

#endif
#define ANALOG 1
#define DIGITAL 0
#define NULL 0

#include <pin.h>

#if (ARDUINO >= 100)
#include <Arduino.h>
#else
#include <WProgram.h>
#endif

// =================================
//	Constructors and Destructors
// =================================

Pin::Pin(String _name, String _api, int _pin, boolean _type, boolean _mode) {
	name		= _name;
	api			= _api;
	pin			= _pin;
	type		= _type;
	mode		= _mode;
	
	updated 	= millis();
	cooldown 	= 500;
	
	pinMode(pin, mode);
}

Pin::Pin(String _name, String _api, int _pin, boolean _type, boolean _mode, int _cooldown) {
	name		= _name;
	api			= _api;
	pin			= _pin;
	type		= _type;
	mode		= _mode;
	cooldown 	= _cooldown;
		
	updated 	= millis();
	pinMode(pin, mode);
}

// ===================
//	Public Methods
// ===================

int Pin::get() {
	if (mode == OUTPUT) {
		Serial.println("Error: Trying to get an output pin.");
		return 0;
	}
  	
	read();
  	return value;
}

void Pin::set(int _value) {
	if (mode == INPUT) {
		Serial.println("Error: Trying to set an input pin.");
		return;
	}
	
	value = _value;
	write();
}

void Pin::update() {
	if (mode == OUTPUT) {
		write();
	} else {
		read();
	}
}

void Pin::print() {
	Serial.println(name + ": " + get());
}

// ====================
//	Private Methods
// ====================

void Pin::read() {
	if (mode == OUTPUT) {
		Serial.println("Error: Trying to read an output pin '" + name + ".'");
		return;
	}
  
	if (millis() - updated < cooldown) {
		Serial.println("Skipping read due to cooldown for pin '" + name + ".'");
		return;
	}
	
	if (type == ANALOG) {
		value = analogRead(pin);
	} else {
		value = digitalRead(pin);
	}
}

void Pin::write() {
	if (mode == INPUT) {
		Serial.println("Error: Trying to write an input  pin '" + name + ".'");
		return;
	}
  
	if (type == ANALOG) {
		analogWrite(pin, value);
	} else {
		digitalWrite(pin, value);
	}
  
	updated = millis();
}
#define ANALOG 1
#define DIGITAL 0
#define NULL 0

#include <bargraph.h>

#if (ARDUINO >= 100)
#include <Arduino.h>
#else
#include <WProgram.h>
#endif

// =================================
//	Constructors and Destructors
// =================================

Bargraph::Bargraph(String _name, String _api, String _max, int _device) {
	name		= _name;
	api			= _api;
	max			= _max;
	device		= _device;
	
	type		= "Default";
}

Bargraph::Bargraph(String _name, String _api, String _max, int _device, String _type) {
	name		= _name;
	api			= _api;
	max			= _max;
	device		= _device;
	type		= _type;	
}

// ===================
//	Public Methods
// ===================

void Bargraph::set(long _value) {
	value = _value;
	
	format();
	update();
}

void Bargraph::update() {
	write();
}

void Bargraph::print() {
	Serial.println(name + ":");
	Serial.println("Value: " + String(value) + ", Formatted: " + formatted);
}

// ====================
//	Private Methods
// ====================

void Bargraph::format() {
	
	
}

void Bargraph::write() {
	
	
	
}
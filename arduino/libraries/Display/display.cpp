#define ANALOG 1
#define DIGITAL 0
#define NULL 0

#include <display.h>
#include <LedControl.h>

#if (ARDUINO >= 100)
#include <Arduino.h>
#else
#include <WProgram.h>
#endif

// =================================
//	Constructors and Destructors
// =================================

Display::Display(String _name, String _api ) {
	name		= _name;
	
	
}

Display::Display(String _name, String _api) {
	name		= _name;
	
	
}

// ===================
//	Public Methods
// ===================

void Display::set(long _value) {
	
	
	format();
	update();
}

void Display::update() {
	
	
	
	write();
}

void Display::print() {
	Serial.println(name + ":");
	Serial.println("Value: " + String(value) + ", Formatted: " + formatted);
}

// ====================
//	Private Methods
// ====================

void Display::format() {
	
	
}

void Display::write() {
	
	
	
}
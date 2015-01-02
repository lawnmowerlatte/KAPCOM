#define ANALOG 1
#define DIGITAL 0
#define NULL 0

#include <pin.h>
#include <pinio.h>
#include <lockedinput.h>

#if (ARDUINO >= 100)
#include <Arduino.h>
#else
#include <WProgram.h>
#endif

// =================================
//	Constructors and Destructors
// =================================

LockedInput::LockedInput(String _name, String _api, int _lock, int _button, int _indicator) : lock(_name + " Locked", "", _lock, DIGITAL, INPUT_PULLUP), button(_name + " Button", "", _button, DIGITAL, INPUT_PULLUP), indicator(_name + " Indicator", "", _indicator, DIGITAL, OUTPUT) {
	name		= _name;
	api			= _api;
	
	update();
	last_value = value;
}

// ===================
//	Public Methods
// ===================

int LockedInput::get() {
	// Update the hardware and return the object value
	
	update();
	return value;
}

void LockedInput::update() {
	// Update the object value based on the hardware Pins
	
	int isLocked = lock.get();
	indicator.set(isLocked);
	
	if (isLocked == LOW) {
		value = 0;
		button.update();
	} else {
		value = button.get();
	}
}

bool LockedInput::updated() {
	// Return true if the value has changed since last updated()
	bool is_updated = (last_value != value);
	last_value = value;
	return is_updated;
}

void LockedInput::print() {
	// Print the name of the pin and the value.
	// Does not force a hardware refresh.
	
	Serial.println(name + ": " + (String)value);
	lock.print();
	button.print();
	indicator.print();
}
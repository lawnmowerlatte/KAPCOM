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
	value		= 0;
}

// ===================
//	Public Methods
// ===================

int LockedInput::get() {
	update();
	return value;
}

void LockedInput::update() {
	int isLocked = lock.get();
	indicator.set(isLocked);
	
	if (isLocked == LOW) {
		Serial.println("Lock engaged");
		value = 0;
		button.update();
	} else {
		Serial.println("Lock disengaged");
		value = button.get();
	}
}

void LockedInput::print() {
	Serial.println(name + ": " + (String)value);
	lock.print();
	button.print();
	indicator.print();
}
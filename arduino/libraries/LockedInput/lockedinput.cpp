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

LockedInput::LockedInput(String _name, String _api, int _lock_in, int _lock_out, int _button_in, int _button_out) : lock(_name + " Locked", "", _lock_in, _lock_out), button(_name + " Button", "", _button_in, _button_out) {
	name		= _name;
	api			= _api;
}

// ===================
//	Public Methods
// ===================

void LockedInput::update() {
	lock.update();
	button.update();
}

void LockedInput::print() {
	Serial.println(name + ":");
	Serial.println("Lock:");
	lock.print();
	Serial.println("Button:");
	button.print();
}
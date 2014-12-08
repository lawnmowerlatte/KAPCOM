#define ANALOG 1
#define DIGITAL 0
#define NULL 0

#include <pin.h>
#include <pinio.h>

#if (ARDUINO >= 100)
#include <Arduino.h>
#else
#include <WProgram.h>
#endif

// =================================
//	Constructors and Destructors
// =================================

PinIO::PinIO(String _name, int _in, int _out) : in(_name + " In", _in, DIGITAL, INPUT, 0), out(_name + " Out", _out, DIGITAL, OUTPUT, 0) {
	name		= _name;
}

// ===================
//	Public Methods
// ===================

void PinIO::update() {
	in.update();
	out.update();
}

void PinIO::print() {
	Serial.println(name + ":");
	Serial.println("In: Pin: " + String((int) in.pin) + ", State: " + String((int) in.get()));
	Serial.println("Out: Pin: " + String((int) out.pin) + ", State: " + String((int) out.get()));
}
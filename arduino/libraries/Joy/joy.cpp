#define ANALOG 1
#define DIGITAL 0
#define NULL 0

#include <joy.h>
#include <pin.h>

#if (ARDUINO >= 100)
#include <Arduino.h>
#else
#include <WProgram.h>
#endif

// =================================
//	Constructors and Destructors
// =================================

Joy::Joy(String _name, int _x, int _y, int _z, int _button, bool _invertX, bool _invertY, bool _invertZ,  int _min, int _max) : x(_name + "x", "", _x, ANALOG, INPUT, "Float", 0, _min, _max, _invertX), y(_name + "y", "", _y, ANALOG, INPUT, "Float", 0, _min, _max, _invertY), z(_name + "z", "", _z, ANALOG, INPUT, "Float", 0, _min, _max, _invertZ), button(_name + " Button", "", _button, DIGITAL, INPUT_PULLUP, "Value", 0) {
	// Set variables
	name		= _name;
	scale		= 2;
}

// ===================
//	Public Methods
// ===================

void Joy::update() {
	// Refresh the hardware, get the values and scale appropriately
	
	// Refresh each axis
	x.update();
	y.update();
	z.update();
	button.update();
	
	// Set each axis to a value from -1 to 1
	X = (x.getFloat()*2.0)-1.0;
	Y = (y.getFloat()*2.0)-1.0;
	Z = (z.getFloat()*2.0)-1.0;
	
	// If it's within 5% of the center, center the input
	if (X >= -.05 && X <= .05) { X = 0; }
	if (Y >= -.05 && Y <= .05) { Y = 0; }
	if (Z >= -.05 && Z <= .05) { Z = 0; }

	// If it's below 5%, set to minimum
	if (X < -.95) { X = -1.0; }
	if (Y < -.95) { Y = -1.0; }
	if (Z < -.95) { Z = -1.0; }

	// If it's above 95%, set to maximum
	if (X > .95) { X = 1.0; }
	if (Y > .95) { Y = 1.0; }
	if (Z > .95) { Z = 1.0; }
	
	// Detect if Joystick is centered
	if (X == 0 && Y == 0 && Z == 0) {
		center = true;
	} else {
		center = false;
	}
	
	// If the button is pressed, reduce range
	if (button.get() == 0) {
		X = X / scale;
		Y = Y / scale;
		Z = Z / scale;
	}
}

bool Joy::centered() {
	return center;
}

// void Joy::print() {
// 	// Print the name of the pin and the value
// 	// Does not force a hardware refresh
//
// 	Serial.println(name + ":");
// 	Serial.println("X: Raw: " + String(x.get()) + ", Raw: " + String(x.getFloat()) + ", Corrected " + String(X));
// 	Serial.println("Y: Raw: " + String(y.get()) + ", Raw: " + String(y.getFloat()) + ", Corrected " + String(Y));
// 	Serial.println("Z: Raw: " + String(z.get()) + ", Raw: " + String(z.getFloat()) + ", Corrected " + String(Z));
// }

// String Joy::toString() {
// 	return String(X) + F(",") + String(Y) + F(",") + String(Z);
// }
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

Joy::Joy(String _name, int _x, int _y, int _z) : x(_name + "x", _x, ANALOG, INPUT, 0), y(_name + "y", _y, ANALOG, INPUT, 0), z(_name + "z", _z, ANALOG, INPUT, 0) {
	name		= _name;
	
	min			= 225;
	max 		= 505;
	scale		= 255;
}

Joy::Joy(String _name, int _x, int _y, int _z, int _min, int _max) : x(_name + "x", _x, ANALOG, INPUT, 0), y(_name + "y", _y, ANALOG, INPUT, 0), z(_name + "z", _z, ANALOG, INPUT, 0) {
	name		= _name;
	
	min 		= _min;
	max 		= _max;
	scale		= 255;
}

// ===================
//	Public Methods
// ===================

void Joy::update() {
	x.update();
	y.update();
	z.update();
	
	X = (x.get()-min)*1.0/(max-min)*100; 
	Y = (y.get()-min)*1.0/(max-min)*100; 
	Z = (z.get()-min)*1.0/(max-min)*100;

	// If it's within 5% of the center, center the input
	//return;
	if (X >= 45 && X <= 55) { X = 50; }
	if (Y >= 45 && Y <= 55) { Y = 50; }
	if (Z >= 45 && Z <= 55) { Z = 50; }

	// If it's close to (or past) 0, set to 0
	if (X < 5) { X = 0; }
	if (Y < 5) { Y = 0; }
	if (Z < 5) { Z = 0; }

	// If it's close to (or past) 100, set to 100
	if (X > 95) { X = 100; }
	if (Y > 95) { Y = 100; }
	if (Z > 95) { Z = 100; }
	
	// Adjust to scale
	X = X / 100.0 * scale;
	Y = Y / 100.0 * scale;
	Z = Z / 100.0 * scale;
}

void Joy::print() {
	Serial.println(name + ":");
	Serial.println("X: Pin: " + String(x.pin) + ", Raw: " + String(x.get()) + ", Adjusted " + String(X));
	Serial.println("Y: Pin: " + String(y.pin) + ", Raw: " + String(y.get()) + ", Adjusted " + String(Y));
	Serial.println("Z: Pin: " + String(z.pin) + ", Raw: " + String(z.get()) + ", Adjusted " + String(Z));
}
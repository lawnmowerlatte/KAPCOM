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

Joy::Joy(String _name, int _x, int _y, int _z) : x(_name + "x", "", _x, ANALOG, INPUT, 0), y(_name + "y", "", _y, ANALOG, INPUT, 0), z(_name + "z", "", _z, ANALOG, INPUT, 0) {
	// Set variables
	name		= _name;
	
	min			= 225;
	max 		= 505;
	scale		= 255;
	
	xMin		= min;
	yMin		= min;
	zMin		= min;
	
	xMax		= max;
	yMax		= max;
	zMax		= max;
}

Joy::Joy(String _name, int _x, int _y, int _z, int _min, int _max) : x(_name + "x", "", _x, ANALOG, INPUT_PULLUP, 0), y(_name + "y", "", _y, ANALOG, INPUT_PULLUP, 0), z(_name + "z", "", _z, ANALOG, INPUT_PULLUP, 0) {
	// Set variables
	name		= _name;
	
	min 		= _min;
	max 		= _max;
	scale		= 255;
	
	xMin		= min;
	yMin		= min;
	zMin		= min;
	
	xMax		= max;
	yMax		= max;
	zMax		= max;
}

// ===================
//	Public Methods
// ===================

void Joy::recalibrate() {
	// Poll each pin and overwrite minimum and maximum values ALWAYS, this clears any previous calibration
	
	xMin = x.get();
	yMin = y.get();
	zMin = z.get();
	
	xMax = x.get();
	yMax = y.get();
	zMax = z.get();
}

void Joy::calibrate() {
	// Poll each pin and overwrite minimum and/or maximum values if detected
	
	int _x = x.get();
	int _y = y.get();
	int _z = z.get();
	
	xMin = min(xMin, _x);
	yMin = min(yMin, _y);
	zMin = min(zMin, _z);
	
	xMax = max(xMax, _x);
	yMax = max(yMax, _y);
	zMax = max(zMax, _z);
}


void Joy::update() {
	// Refresh the hardware, get the values and scale appropriately
	
	// Refresh each axis
	x.update();
	y.update();
	z.update();
	
	// Set each axis to a value out of 100
	X = (x.get()-xMin)*1.0/(xMax-xMin)*100; 
	Y = (y.get()-yMin)*1.0/(yMax-yMin)*100; 
	Z = (z.get()-zMin)*1.0/(zMax-zMin)*100;

	// If it's within 5% of the center, center the input
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
	
	if (X >= 45 && X <= 55 && Y >= 45 && Y <= 55 && Z >= 45 && Z <= 55) {
		center = true;
	} else {
		center = false;
	}
	
	// Adjust to scale
	X = X / 100.0 * scale;
	Y = Y / 100.0 * scale;
	Z = Z / 100.0 * scale;
}

bool Joy::centered() {
	return center;
}

void Joy::print() {
	// Print the name of the pin and the value
	// Does not force a hardware refresh
	
	Serial.println(name + ":");
	Serial.println("X: Raw: " + String(x.get()) + " (" + xMin + "-" + xMax + "), Adjusted " + String(X));
	Serial.println("Y: Raw: " + String(y.get()) + " (" + yMin + "-" + yMax + "), Adjusted " + String(Y));
	Serial.println("Z: Raw: " + String(z.get()) + " (" + zMin + "-" + zMax + "), Adjusted " + String(Z));
}
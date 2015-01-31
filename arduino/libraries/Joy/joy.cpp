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

Joy::Joy(String _name, int _x, int _y, int _z, int _button) : x(_name + "x", "", _x, ANALOG, INPUT, 0), y(_name + "y", "", _y, ANALOG, INPUT, 0), z(_name + "z", "", _z, ANALOG, INPUT, 0), button(_name + " Button", "", _button, DIGITAL, INPUT_PULLUP, 0) {
	// Set variables
	name		= _name;
	
	min			= 225;
	max 		= 505;
	scale		= 2;
	
	xMin		= min;
	yMin		= min;
	zMin		= min;
	
	xMax		= max;
	yMax		= max;
	zMax		= max;
}

Joy::Joy(String _name, int _x, int _y, int _z, int _button, int _min, int _max) : x(_name + "x", "", _x, ANALOG, INPUT_PULLUP, 0), y(_name + "y", "", _y, ANALOG, INPUT_PULLUP, 0), z(_name + "z", "", _z, ANALOG, INPUT_PULLUP, 0), button(_name + " Button", "", _button, DIGITAL, INPUT_PULLUP, 0) {
	// Set variables
	name		= _name;
	
	min 		= _min;
	max 		= _max;
	scale		= 2;
	
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
	
	xMin = x.get() - 1;
	yMin = y.get() - 1;
	zMin = z.get() - 1;
	
	xMax = x.get() + 1;
	yMax = y.get() + 1;
	zMax = z.get() + 1;
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
	
	if (xMin = xMax) {
		xMin--;
		xMax++;
	}
	if (yMin = yMax) {
		yMin--;
		yMax++;
	}
	if (zMin = zMax) {
		zMin--;
		zMax++;
	}
}


void Joy::update() {
	// Refresh the hardware, get the values and scale appropriately
	
	// Refresh each axis
	x.update();
	y.update();
	z.update();
	
	// Set each axis to a value out of 100
	X = (x.get()-xMin)*1.0/(xMax-xMin)*10000; 
	Y = (y.get()-yMin)*1.0/(yMax-yMin)*10000; 
	Z = (z.get()-zMin)*1.0/(zMax-zMin)*10000;

	// If it's within 5% of the center, center the input
	if (X >= 4500 && X <= 5500) { X = 5000; }
	if (Y >= 4500 && Y <= 5500) { Y = 5000; }
	if (Z >= 4500 && Z <= 5500) { Z = 5000; }

	// If it's close to (or past) 0, set to 0
	if (X < 500) { X = 0; }
	if (Y < 500) { Y = 0; }
	if (Z < 500) { Z = 0; }

	// If it's close to (or past) 100, set to 100
	if (X > 9500) { X = 10000; }
	if (Y > 9500) { Y = 10000; }
	if (Z > 9500) { Z = 10000; }
	
	if (X >= 4500 && X <= 5500 && Y >= 4500 && Y <= 5500 && Z >= 4500 && Z <= 5500) {
		center = true;
	} else {
		center = false;
	}
	
	// Adjust to scale
	X = (X / 5000.0) - 1;
	Y = (Y / 5000.0) - 1;
	Z = (Z / 5000.0) - 1;
	
	// If the button is pressed, reduce range
	if (button.get() == 1) {
		X = X / scale;
		Y = Y / scale;
		Z = Z / scale;
	}
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

String Joy::toString() {
	return String(X) + "," + String(Y) + "," + String(Z);
}
#define OFF 0
#define RED 1
#define YELLOW 2
#define GREEN 3

#include <Wire.h>
#include "Adafruit_LEDBackpack.h"
#include "Adafruit_GFX.h"
#include <bargraph.h>

#if (ARDUINO >= 100)
#include <Arduino.h>
#else
#include <WProgram.h>
#endif

// =================================
//	Constructors and Destructors
// =================================

Bargraph::Bargraph(String _name, String _api, String _max, int _device, String _type) {
	name		= _name;
	api			= _api;
	max			= _max;
	device		= _device;
	type		= _type;
	value		= 0;
	
	display		= { OFF, OFF, OFF, OFF, OFF, OFF,
		 			OFF, OFF, OFF, OFF, OFF, OFF,
					OFF, OFF, OFF, OFF, OFF, OFF };
	
	bar = Adafruit_24bargraph();
	bar.begin(0x70+device);
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
	for (int i=0; i<24; i++) {
		bar.setBar(i, 0);
	}
	
	if (type == "Default") {
		float percent = (value * 100.0) / max;
		int color = 0;
		
		if (p > 50)				{	color = green;	}
		if (p <= 50 && p > 20)	{	color = yellow;	}
		if (p <= 20 && p > 0)	{	color = red;	}
		
		for (int i=0; i<int(percent); i++) {
			display[i] = color;
		}
	}
}

void Bargraph::write() {
	for (int i=0; i<24; i++) {
		bar.setBar(i, display[i]);
	}

    bar.writeDisplay();
}
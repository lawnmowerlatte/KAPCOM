#define OFF 0
#define RED 1
#define YELLOW 2
#define GREEN 3

#include <bargraph.h>

#if (ARDUINO >= 100)
#include <Arduino.h>
#else
#include <WProgram.h>
#endif

// =================================
//	Constructors and Destructors
// =================================

Bargraph::Bargraph(String _name, String _api, int _device, String _type) : bar() {
	name		= _name;
	api			= _api;
	device		= _device;
	type		= _type;
	value		= 0;
	
	for (int i=0; i<24; i++) {
		display[i] = OFF;
	}
	
	bar.begin(0x70+device);
}

// ===================
//	Public Methods
// ===================

void Bargraph::set(String _value) {
	value = _value.toInt();
	
	format();
	update();
}

void Bargraph::setMax(String _max) {
	max = _max.toInt();
}

void Bargraph::update() {
	write();
}

void Bargraph::print() {
	Serial.println(name + ":");
	Serial.println("Value: " + String(value) + ", Type: " + type);
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
		
		if (percent > 50)					{	color = GREEN;	}
		if (percent <= 50 && percent > 20)	{	color = YELLOW;	}
		if (percent <= 20 && percent > 0)	{	color = RED;	}
		
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
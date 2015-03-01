#define ANALOG 1
#define DIGITAL 0
#define NULL 0

#include <pin.h>

#if (ARDUINO >= 100)
#include <Arduino.h>
#else
#include <WProgram.h>
#endif

// =================================
//	Constructors and Destructors
// =================================

Pin::Pin(String _name, String _api, int _pin, boolean _type, boolean _mode, String _format, int _cooldown, int _min, int _max, int _invert) {
	// Set variables
	name		= _name;
	api			= _api;
	pin			= _pin;
	type		= _type;
	mode		= _mode;
	format		= _format;
	min			= _min;
	max			= _max;
	invert		= _invert;
	cooldown 	= _cooldown;
	
	// Initialize the pin
	pinMode(pin, mode);
	
	// Set default value, update from hardware, set initial value of previous
	value = 0;
	fvalue = 0;
	update();
	
	// Set the previous values
	last_update = millis();
	last_value = value;
	
	if (format==F("Key")) {
		key = api;
		api = F("KEY");
	}
}

// ===================
//	Public Methods
// ===================

int Pin::get() {
	// Read the hardware and return the object value
	update();
	
	if (mode == OUTPUT) {
		// Serial.println("Error: Trying to get an output pin.");
		return 0;
	} else {
		return value;
	}
}

float Pin::getFloat() {
	// Read the hardware and return the object value
	update();
	
	if (mode == OUTPUT) {
		// Serial.println("Error: Trying to get an output pin.");
		return 0;
	} else {
		return fvalue;
	}
}

void Pin::set(int _value) {
	// Set the object value and write it to the hardware
	
	if (mode == INPUT) {
		// Serial.println("Error: Trying to set an input pin.");
		return;
	}
	
	value = _value;
	update();
}

void Pin::set(String _value) {
	// Determine value based on string input

	if (_value == F("1"))		{ set(1); return; }
	if (_value == F("0"))		{ set(0); return; }
	if (_value == F("True"))	{ set(1); return; }
	if (_value == F("False"))	{ set(0); return; }
}

void Pin::update() {
	// Force a refresh of the values
	// Can be safely called on both INPUT and OUTPUT pins
	
	if (mode == OUTPUT) {
		write();
	} else {
		read();
	}
}

bool Pin::changed() {
	// Return true if the value has changed since last updated()
	
	bool is_updated = (last_value != value);
	last_value = value;
	return is_updated;
}

String Pin::toString() {
	String t=F("True");
	String f=F("False");
	String none=F("None");
	String blank=F("");
	
	
	if (mode == OUTPUT) {
		Serial.println(F("Error: Trying to get an output pin."));
		return blank;
	}
	
	if (format == F("Value")) {
		return String(value);
	}
	
	if (format == F("Toggle")) {
		if (value == 1) {
			return none;
		} else {
			return blank;
		}
	}
	
	if (format == F("TrueFalse")) {
		if (value == 0) {
			return f;
		} else {
			return t;
		}
	}
	
	if (format == F("True")) {
		if (value == 1) {
			return t;
		} else {
			return blank;
		}
	}
	
	if (format == F("False")) {
		if (value == 0) {
			return f;
		} else {
			return blank;
		}
	}
	
	if (format == F("Zero")) {
		if (value == 0) {
			return F("0");
		} else {
			return blank;
		}
	}
	
	if (format == F("One")) {
		if (value == 1) {
			return F("1");
		} else {
			return blank;
		}
	}
	
	if (format == F("Key")) {
		if (value == 1) {
			return key;
		} else {
			return blank;
		}
	}
	
	if (format == F("Float")) {
		return String(fvalue);
	}
	
	if (format == F("Percent")) {
		return String(fvalue*100.0);
	}
	
	// Serial.println("Unexpected format \"" + format + "\" in object \"" + name + "\"");
	Serial.println(F("Unexpected format"));
	return F("Error");
}

// void Pin::print() {
// 	// Print the name of the pin and the value.
// 	// Does not force a hardware refresh.
//
// 	Serial.println(name + ": " + value + ", (" + fvalue + ")");
// }

// ====================
//	Private Methods
// ====================

void Pin::read() {
	// Poll the hardware and set the object value
	
	if (mode == OUTPUT) {
		// Serial.println("Error: Trying to read an output pin '" + name + ".'");
		return;
	}
  
  	// Skip a hardware poll if the button was recently pushed
	if (millis() - last_update < cooldown) {
		// Serial.println("Skipping read due to cooldown for pin '" + name + ".'");
		return;
	}
	
	if (type == ANALOG) {
		value = analogRead(pin);
		fvalue = (value-min)*1.0/(max-min);
		
		if (invert) {
			value = 1 - value;
		}
	} else {
		value = digitalRead(pin);
	}
	
	last_update = millis();
}

void Pin::write() {
	// Update the hardware with the latest object value
	
	if (mode == INPUT) {
		// Serial.println("Error: Trying to write an input  pin '" + name + ".'");
		return;
	}
  
	if (type == ANALOG) {
		analogWrite(pin, value);
	} else {
		digitalWrite(pin, value);
	}
  
	last_update = millis();
}
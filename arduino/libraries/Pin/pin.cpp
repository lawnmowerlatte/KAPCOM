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
	
	if (format=="Key") {
		key = api;
		api = "KEY" + key;
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
	if (mode == OUTPUT) {
		Serial.println("Error: Trying to get an output pin.");
		return "";
	}
	
	if (format == "Value") {
		return String(value);
	}
	
	if (format == "Toggle") {
		if (value == 1) {
			return "None";
		} else {
			return "";
		}
	}
	
	if (format == "TrueFalse") {
		if (value == 0) {
			return "False";
		} else {
			return "True";
		}
	}
	
	if (format == "True") {
		if (value == 1) {
			return "True";
		} else {
			return "";
		}
	}
	
	if (format == "False") {
		if (value == 0) {
			return "False";
		} else {
			return "";
		}
	}
	
	if (format == "Zero") {
		if (value == 0) {
			return "0";
		} else {
			return "";
		}
	}
	
	if (format == "One") {
		if (value == 1) {
			return "1";
		} else {
			return "";
		}
	}
	
	if (format == "Key") {
		if (value == 1) {
			return key;
		} else {
			return "";
		}
	}
	
	if (format == "Float") {
		return String(fvalue);
	}
	
	if (format == "Percent") {
		return String(fvalue*100.0);
	}
	
	Serial.println("Unexpected format \"" + format + "\" in object \"" + name + "\"");
	return "Error";
}

void Pin::print() {
	// Print the name of the pin and the value.
	// Does not force a hardware refresh.
	
	Serial.println(name + ": " + value + ", (" + fvalue + ")");
}

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
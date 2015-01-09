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

Pin::Pin(String _name, String _api, int _pin, boolean _type, boolean _mode) {
	// Set variables
	name		= _name;
	api			= _api;
	pin			= _pin;
	type		= _type;
	mode		= _mode;
	strings		= false;
	
	// Set the cooldown counters
	last_update = millis();
	cooldown 	= 500;
	
	// Initialize the pin
	pinMode(pin, mode);
	
	// Set default value, update from hardware, set initial value of previous
	value = 0;
	update();
	last_value = value;
}

Pin::Pin(String _name, String _api, int _pin, boolean _type, boolean _mode, bool _strings) {
	// Set variables
	name		= _name;
	api			= _api;
	pin			= _pin;
	type		= _type;
	mode		= _mode;
	strings		= _strings;
	
	// Set the cooldown counters
	last_update = millis();
	cooldown 	= 500;
	
	// Initialize the pin
	pinMode(pin, mode);
	
	// Set default value, update from hardware, set initial value of previous
	value = 0;
	update();
	last_value = value;
}

Pin::Pin(String _name, String _api, int _pin, boolean _type, boolean _mode, int _cooldown) {
	// Set variables
	name		= _name;
	api			= _api;
	pin			= _pin;
	type		= _type;
	mode		= _mode;
	strings		= false;
	
	// Set the cooldown counters
	last_update = millis();
	cooldown 	= _cooldown;
	
	// Initialize the pin
	pinMode(pin, mode);
	
	// Set default value, update from hardware, set initial value of previous
	value = 0;
	update();
	last_value = value;
}

Pin::Pin(String _name, String _api, int _pin, boolean _type, boolean _mode, int _cooldown, bool _strings) {
	// Set variables
	name		= _name;
	api			= _api;
	pin			= _pin;
	type		= _type;
	mode		= _mode;
	strings		= _strings;
	
	// Set the cooldown counters
	last_update = millis();
	cooldown 	= _cooldown;
	
	// Initialize the pin
	pinMode(pin, mode);
	
	// Set default value, update from hardware, set initial value of previous
	value = 0;
	update();
	last_value = value;
}

// ===================
//	Public Methods
// ===================

int Pin::get() {
	// Read the hardware and set the object value
	
	if (mode == OUTPUT) {
		// Serial.println("Error: Trying to get an output pin.");
		return 0;
	} else {
		return value;
	}
}

String Pin::toString() {
	if (mode == OUTPUT) {
		// Serial.println("Error: Trying to get an output pin.");
		return "";
	} else {
		if (strings) {
			if (value == 1) {
				return "True";
			} else {
				return "False";
			}
		} else if (value == 0) {
			return "False";
		} else {
			return String(value);
		}		
	}
}

void Pin::set(int _value) {
	// Set the object value and write it to the hardware
	
	if (mode == INPUT) {
		// Serial.println("Error: Trying to set an input pin.");
		return;
	}
	
	value = _value;
	write();
}

bool Pin::updated() {
	// Return true if the value has changed since last updated()
	
	bool is_updated = (last_value != value);
	last_value = value;
	return is_updated;
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

void Pin::print() {
	// Print the name of the pin and the value.
	// Does not force a hardware refresh.
	
	Serial.println(name + ": " + value);
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
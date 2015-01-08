#define ANALOG 1
#define DIGITAL 0
#define NULL 0

#include <display.h>
#include <LedControl.h>

#if (ARDUINO >= 100)
#include <Arduino.h>
#else
#include <WProgram.h>
#endif

// =================================
//	Constructors and Destructors
// =================================

Display::Display(String _name, String _api, LedControl _l, int _length, int _device) : l(_l) {
	// Set variables
	name		= _name;
	api			= _api;
	length		= _length;
	device		= _device;
	
	offset		= 0;
	decimals	= 2;
	pad			= " ";
}

Display::Display(String _name, String _api, LedControl _l, int _length, int _device, int _offset, int _decimals, String _pad) : l(_l) {
	// Set variables
	name		= _name;
	api			= _api;
	length		= _length;
	device		= _device;
	offset		= _offset;
	decimals	= _decimals;
	pad			= _pad;
}

// ===================
//	Public Methods
// ===================

void Display::set(String _value) {
	// Set the value in the object, format it and update the display
	value = _value;
	
	format();
	update();
}

void Display::update() {
	// Alias for private write() method
	write();
}

void Display::print() {
	Serial.println(name + ":");
	Serial.println("Value: " + value + ", Formatted: " + formatted);
}

// ====================
//	Private Methods
// ====================

void Display::format() {
	// Take the value passed and format it for the 8 digit seven-segment display
	
	// Broken down components of the final formatted string
	String integer, decimal, E;
	// Counter for exponents when using scientific notation
	int exponent = 0;
	
	// Break the value into integer and decimal portions
	integer = value.substring(0, value.indexOf('.'));
	decimal = value.substring(value.indexOf('.'));
	
	if (integer.length() > length) {
		// More integers than can be displayed
		// Use scientific notation
		
		// Start with base of 1K
		exponent = 3;
		
		// Loop until the integer length is less than the display length
		while (integer.length()+E.length()+1 > length) {
			// Increment by 1K
			exponent += 3;
			
			// Reset integers
			integer = value.substring(0, value.indexOf('.'));
			// Truncate integers based on current exponent
			integer = integer.substring(0, integer.length()-exponent);
		}
		
		// Convert exponent to string
		E = String(exponent);
		// Truncate decimals to fit in remaining digits
		decimal = decimal.substring(0, length-integer.length()-E.length()-1);
		// Create formatted string
		formatted = integer + "." + decimal + "E" + E;
		
	} else if (integer.length() < length) {
		// Fewer integers than can be displayed
		// Attempt to fill with decimals
		
		// Truncate the decimals to fit on the display
		decimal = decimal.substring(0, length-integer.length());
		
		// Truncate the decimals according to maximum decimal length
		if (decimal.length() > decimals) {
			decimal = decimal.substring(0, decimals);
		}
		
		// Create formatted string
		formatted = integer + "." + decimal;
		
	} else {
		// Itegers fill display
		formatted = integer;
	}
	
	// Pad string if it's too short
	for (int i=0; i < formatted.length() - length; i++) {
		formatted = pad + formatted;
	}
	
	// Final check for string length
	if (formatted.length() != length) {
		// Print a debug message
		Serial.println("Something went wrong while formatting " + value + ". Formatted value " + formatted + " does not fit available length.");
		
		// Set the display to dashes
		formatted = "";
		for (int i=0; i<length; i++) {
			formatted = formatted + "-";
		}
	}
}

void Display::write() {
	// Write formatted value to LedControl object
	
	// Stores whether to display the decimal point with the current character
	bool point;
	
	for (int i=0; i<formatted.length(); i++) {
		point = false;
		// Detect decimal point in next character
		if (formatted.charAt(i+1) == '.') {
			point = true;
		}
		
		// Write the character to the display
		l.setDigit(device, 7-offset-i, formatted.charAt(i), point);
		
		// If decimal was detected in the next character, skip it
		if (point) {
			i++;
		}
	}
}
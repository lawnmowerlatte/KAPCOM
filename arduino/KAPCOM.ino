#include <LedControl.h>
#include <Wire.h>
#include <Adafruit_LEDBackpack.h>
#include <Adafruit_GFX.h>

int DIN=7;
int CLK=6;
int LOAD=5;
int DISPLAY_COUNT=5;
LedControl displays=LedControl(DIN,CLK,LOAD,DISPLAY_COUNT);

const int BARGRAPH_COUNT=5;
Adafruit_24bargraph bargraphs[BARGRAPH_COUNT];

void digitalReader(int pin) {
  Serial.println(digitalRead(pin));
}

void digitalWriter(int pin, byte data) {
  if (data <= 1) {
    digitalWrite(pin, data);
  } else {
    Serial.println("Bad data for digital write: " + data);
  }
}

void analogReader(int pin) {
  Serial.println(analogRead(pin));
}

void analogWriter(int pin, byte data) {
  analogWrite(pin, data);
}

void displayWriter(int device, String data) {
  bool point;

  for (int i=0; i<data.length(); i++) {
    point = false;
    // Detect decimal point in next character
    if (data.charAt(i+1) == '.') {
      point = true;
    }
		
    // Write the character to the display
    displays.setDigit(device, 7-i, data.charAt(i), point);
		
    // If decimal was detected in the next character, skip it
    if (point) {
      i++;
    }
  }
  
}

void bargraphWriter(int device, String data) {
  char red[3];
  char green[3];
  int r, g, v;
  
  memcpy(red, &data.c_str()[0], 3);
  memcpy(green, &data.c_str()[3], 3);
  
  for (int i=0; i<3; i++) {
    for (int j=0; j<8; j++) {
        r = bitRead(red[i], j);
        g = bitRead(green[i], j);
        
        v=0;
        if (r==1 && g==1) {
          v=2;
        } else if (r==1) {
          v=1;
        } else if (g==1) {
          v=3;
        }
        
        bargraphs[device].setBar(i*j, v);
    }
  }
  
  bargraphs[device].writeDisplay();
}

void pinModify(int pin, byte data){
  switch (data) {
    case 0:
      pinMode(pin, OUTPUT);
      break;
    case 1:
      pinMode(pin, INPUT);
      break;
    case 2:
      pinMode(pin, INPUT_PULLUP);
      break;
    default:
      Serial.println("Bad data for pin mode: " + data);
  }
}

void serialEvent() {
  char readChar[64];
  Serial.readBytesUntil(33,readChar,64);
  String read_ = String(readChar);
  
  // Retrieve components 
  String cmd = read_.substring(1,2);
  int id = int(read_.substring(2,2).c_str());
  String data = read_.substring(3);
  
  // Branch based on command
  if (cmd == "pm") {
    pinModify(id, data[0]);   
  } else if (cmd == "dw") {
    digitalWriter(id, data[0]);   
  } else if (cmd == "dr") {
    digitalReader(id);   
  } else if (cmd == "aw") {
    analogWriter(id, data[0]);   
  } else if (cmd == "ar") {
    analogReader(id);   
  } else if (cmd == "7w") {
    displayWriter(id, data);   
  } else if (cmd == "bw") {
    bargraphWriter(id, data);   
  }
}

void setup()  {
  Serial.begin(115200);
  
  // Initialize the bargraphs
  for (int i=0; i<BARGRAPH_COUNT; i++) {
    bargraphs[i] = Adafruit_24bargraph();
    bargraphs[i].begin(0x70+i);
  }
}

void loop() { }

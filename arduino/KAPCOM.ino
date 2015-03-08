#include <LedControl.h>
#include <Wire.h>
#include <Adafruit_LEDBackpack.h>
#include <Adafruit_GFX.h>

// Global Serial Reading
String readLine;
String nextLine;

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
  char red[4];
  char green[4];
  int r, g, v;
  
  memcpy(red, &data.c_str()[0], 4);
  memcpy(green, &data.c_str()[4], 4);
  
  for (int i=0; i<3; i++) {
    for (int j=2; j<8; j++) {
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
        
        bargraphs[device].setBar(i*6+j-2, v);
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

void(* reset) (void) = 0;

void serialEvent() {
  while (Serial.available()) {
    char c = (char)Serial.read();

    if (c == 255) {
      readLine = nextLine;
      nextLine = "";
      if (readLine == F("RESTART")) {
        Serial.println(F("Resetting..."));
        delay(1000); 
        reset();
      }
    } else {
      nextLine += c;
    }
  }
}

void command(String read_) {
  // Retrieve components 
  char cmd = read_[0];
  int id = read_[1] - 32;
  String data = read_.substring(2);
  
  Serial.println(cmd + " : " + String(id) + " : " + data);
  
  // Switch based on command
  switch (cmd) {
    case 'm':
      pinModify(id, data[0]);
      break;
    case 'd':
      digitalWriter(id, data[0]);
      break;
    case 'D':
      digitalReader(id);
      break;
    case 'a':
      analogWriter(id, data[0]); 
      break;
    case 'A':
      analogReader(id);
      break;
    case '7':
      displayWriter(id, data);
      break;
    case 'b':
      bargraphWriter(id, data);
    default:
      Serial.println("Unknown command: " + cmd);
  }
}

void setup()  {
  Serial.begin(115200);
  
  Serial.println("ONLINE");
  
  // Initialize the bargraphs
  for (int i=0; i<BARGRAPH_COUNT; i++) {
    bargraphs[i] = Adafruit_24bargraph();
    bargraphs[i].begin(0x70+i);
  }
}

void loop() {
  if (readLine !="") {
    Serial.println(readLine);
    command(readLine);
    readLine = "";
  }
}

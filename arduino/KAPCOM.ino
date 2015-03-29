#include "LedControl.h"
#include <Wire.h>
#include <Adafruit_LEDBackpack.h>
#include <Adafruit_GFX.h>

// Global Serial Reading
String readLine;
String nextLine;
String subscriptions;
int analogOffset = A0;

String v = "KAPCOM v0.1";

int DIN=7;
int LOAD=6;
int CLK=5;
int DISPLAY_COUNT=5;
LedControl displays=LedControl(DIN,CLK,LOAD,DISPLAY_COUNT);

const int BARGRAPH_COUNT=5;
Adafruit_24bargraph bargraphs[BARGRAPH_COUNT];

void digitalReader(int pin) {
  if (pin > 160) {
    pin = pin - 160 + analogOffset;
  }
  
  Serial.println(digitalRead(pin));
}

void digitalWriter(int pin, String data) {
  if (pin > 160) {
    pin = pin - 160 + analogOffset;
  }
  
  if (data.toInt() <= 1) {
    digitalWrite(pin, data.toInt());
  } else {
    Serial.println("Bad data for digital write: " + data);
  }
  Serial.println();
}

void analogReader(int pin) {
  Serial.println(analogRead(pin));
}

void analogWriter(int pin, String data) {
  analogWrite(pin, data.toInt());
  Serial.println();
}

void subscribe(String pins) {
  subscriptions = pins;
  
  for (int i=0; i<subscriptions.length(); i++) {
    subscriptions[i] -= 32;
  }
  Serial.println();
}

void sendSubscription() {
  char message[subscriptions.length()];
  
  for (int i=0; i<subscriptions.length(); i++) {
    int id = subscriptions[i];
    int v = 0;
    byte b = 0;
    
    if (id < 160) {
      v = digitalRead(id);
      if (v == 1) {
        v = '1';
      } else {
        v = '0';
      }
    } else {
      id -= 160;
      v = analogRead(id);
      v = v/4;
    }
    
    if (v > 255) {
      v = 255;
    }
    
    b = v;
    message[i]=(char) b;
    
    Serial.print(message[i]);
  }
  Serial.println();
}

void displayWriter(int device, String data) {
  bool point       =  false;
  int  marker      =  0;
  char character   =  ' ';

  for (int i = 0; i < 8; i++) {
    point      =  false;
    character  =  data.charAt(marker);
    
    // Detect decimal point in next character
    if (data.charAt(marker+1) == '.') {
      point = true;
      marker++;
    }
    
    switch (character) {
      case ' ':
      case 'E':
      case '-':
        // Set the character to blank
        displays.setChar(device, 7-i, character, point);
        break;
      default:
        // Write the character to the display
        displays.setDigit(device, 7-i, String(character).toInt(), point);
        break;
    }
    
    marker++;
  }
  Serial.println();
}

void bargraphWriter(int device, String data) {
  char red[4];
  char green[4];
  int r, g, v;
  
  for (int i = 0; i < 4; i++) {
    red[i]    =  data[i];
    green[i]  =  data[i+4];
  }
  
  for (int i=0; i<4; i++) {
    for (int j=0; j<6; j++) {
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
        
        bargraphs[device].setBar(23  -((i*6)+(5-j)), v);
    }
  }
  
  bargraphs[device].writeDisplay();
  Serial.println();
}

void pinModify(int pin, String data) {
  if (pin > 160) {
    pin = pin - 160 + analogOffset;
  }
  
  switch (data.toInt()) {
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
  Serial.println();
}

void getVersion() {
  Serial.println(v);
  Serial.println();
}

void(* reset) (void) = 0;

void serialEvent() {
  while (Serial.available()) {
    char c = (char)Serial.read();

    if (c == 10) {
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
  byte id = read_[1] - 32;
  String data = read_.substring(2);
  
  //Serial.println(String(cmd) + " : " + String(id) + " : " + data);
  
  // Switch based on command
  switch (cmd) {
    case 'm':
      pinModify(id, data);
      break;
    case 'd':
      digitalWriter(id, data);
      break;
    case 'D':
      digitalReader(id);
      break;
    case 'a':
      analogWriter(id, data); 
      break;
    case 'A':
      analogReader(id);
      break;
    case 's':
      subscribe(data);
      break;
    case 'S':
      sendSubscription();
      break;
    case '7':
      id        +=  32;
      displayWriter(String(char(id)).toInt(), data);
      break;
    case 'b':
      id        +=  32;
      bargraphWriter(String(char(id)).toInt(), data);
      break;
    case 'v':
      getVersion();
      break;
    default:
      Serial.println("Unknown command: " + cmd);
  }
}

void setup()  {
  Serial.begin(115200);
  
  // Initialize the bargraphs
  for (int i=0; i<BARGRAPH_COUNT; i++) {
    bargraphs[i] = Adafruit_24bargraph();
    bargraphs[i].begin(0x70+i);
  }
  
  for (int i = 0; i < DISPLAY_COUNT; i++) {
    displays.shutdown(i,false);   // Enable display
    displays.setIntensity(i,10);  // Set brightness level (0 is min, 15 is max)
    displays.clearDisplay(i);     // Clear display register
  } 
}

void loop() {
  if (readLine !="") {
    // Serial.println(readLine);
    command(readLine);
    readLine = "";
  }
}

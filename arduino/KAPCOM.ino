#define ANALOG 1
#define DIGITAL 0
#define NULL 0

#include <pin.h>
#include <pinio.h>
#include <lockedinput.h>
#include <joy.h>

Joy J0("J0", A0, A1, A2);
Joy J1("J1", A4, A5, A6);

Pin soft("Soft", 54+4, DIGITAL, INPUT);
PinIO rcs("RCS", 1, 2);
LockedInput stage("Stage", 3, 4, 5, 6);
LockedInput abandon("Abort", 7, 8, 9, 10);

void setup() {
  Serial.begin(9600);
  
  Serial.println("Calibrating")
  
  while (stage.button.get() == LOW) {
   J0.calibrate();
   J1.calibrate(); 
  }
  
  Serial.println("Ready")
}

void loop() {
  soft.update();
  rcs.update();
  J0.update();
  J1.update();
  
  J0.print();
  J1.print();
  
  String output = "I: " + String(J0.X, HEX) + String(J0.Y, HEX) + String(J0.Z, HEX) + String(J1.X, HEX) + String(J1.Y, HEX) + String(J1.Z, HEX);
  output.toUpperCase();
  
  Serial.println(output);
  //soft.print();
  //rcs.print();
  
  //delay(1000);
}

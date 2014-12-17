#define ANALOG 1
#define DIGITAL 0
#define NULL 0

#include <pin.h>
#include <pinio.h>
#include <lockedinput.h>
#include <joy.h>
#include <ArduinoJson.h>

// Global Serial Reading
char* readLine;
char* nextLine;

// Create joystick objects
Joy J0("J0", A0, A1, A2);
Joy J1("J1", A4, A5, A6);

// Create button objects
//Pin soft("Soft", "?", 54+4, DIGITAL, INPUT_PULLUP);
//PinIO rcs("RCS", "rcs", 1, 2);
LockedInput stage("Stage", "stage", A10, A11, A13);
LockedInput abandon("Abort", "abort", A8, A9, A12);

void setup() {
  // Start the serial connection
  Serial.begin(9600);
  // Report online status
  Serial.println("ONLINE");
  // Receive configuration
  // configure();
  
  // Report calibration status
  Serial.println("CALIBRATING");
  
  
  // Calibrate until the staging button is pressed
  abandon.indicator.set(HIGH);
  stage.indicator.set(HIGH);
  J0.recalibrate();
  J1.recalibrate();
  J0.print();
  J1.print();
  while (abandon.button.get() == LOW) {
    J0.calibrate();
    J1.calibrate();
  }
  abandon.indicator.set(LOW);
  stage.indicator.set(LOW);
  
  // Report ready status
  Serial.println("READY");
}

void(* reset) (void) = 0;

   


void serialEvent() {
  while (Serial.available()) {
    char c = (char)Serial.read();
    
    if (c == '\n') {
      readLine = nextLine;
      nextLine ="";
    } else {
      nextLine += c;
    }
  }
}

void configure() {
  StaticJsonBuffer<512> jsonBuffer;
  char* json = readLine;
  
  // Parse JSON
  JsonObject& configuration = jsonBuffer.parseObject(json);
  if (!configuration.success()) {
    Serial.println("JSON Parsing failed.");
    reset();
  }
  
}

void poll() {
  // Poll all hardware inputs for latest values
  //soft.update();
  //rcs.update();
  J0.update();
  J1.update();
}

void processInput() {
  StaticJsonBuffer<512> jsonBuffer;
  JsonObject& input = jsonBuffer.createObject();
  
  // Aggregate fly-by-wire data
  
  
  
  // Send fly-by-wire data
  input.printTo(Serial);
}

void processOutput() {
  StaticJsonBuffer<512> jsonBuffer;
  char* json = readLine;
  
  // Parse received telemetry
  JsonObject& output = jsonBuffer.parseObject(json);
  if (!output.success()) {
    Serial.println("JSON Parsing failed.");
    reset();
  }
  
  // Update instrumentation panels
  
  
}



void loop() {
  //Serial.println("loop()");
  stage.update();
  abandon.update();
  J0.update();
  J1.update();
  
  stage.print();
  abandon.print();
  //J0.print();
  //J1.print();
  
  delay(1000);
  
  
  
  
  // Wait for telemetry data
  //processOutput();
  // Poll hardware for inputs
  //poll();
  // Send fly-by-wire data
  //processInput();
}

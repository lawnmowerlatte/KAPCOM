#define ANALOG 1
#define DIGITAL 0
#define NULL 0

#include <new.cpp>
#include <iterator>
#include <vector>

#include <LedControl.h>

#include <pin.h>
#include <lockedinput.h>
#include <joy.h>
#include <display.h>
//#include <bargraph.h>
#include <ArduinoJson.h>

using namespace std;

// Global Serial Reading
String readLine = "";
String nextLine = "";

// Create calibration inputs
LockedInput calibrate("Calibrate", "calibrate", 2, 3, 4);

// Create global LedControl
int display_count = 5;
LedControl lc(7, 5, 6, display_count);

// Create vectors and iterators
vector<Joy> joys;
vector<Joy>::iterator joy;

vector<Pin> buttons;
vector<Pin>::iterator button;

vector<Pin> indicators;
vector<Pin>::iterator indicator;
   
vector<LockedInput> locks;
vector<LockedInput>::iterator lock;
/*
vector<Bargraph> bargraphs;
vector<Bargraph>::const_iterator bargraph;

vector<Display> displays;
vector<Display>::const_iterator display;
*/

void(* reset) (void) = 0;

void serialEvent() {
  while (Serial.available()) {
    char c = (char)Serial.read();
    
    if (c == '\n' || c == 10 || c == 13) {
      readLine = nextLine;
      nextLine = "";
      
      if (readLine == "RESTART") {
        Serial.println("Resetting...");
        delay(1000); 
        reset();
      }
    } else {
      nextLine += c;
    }
  }
}

void setup() {
  // Initialize displays
  for(int i=0; i<display_count; i++) {
    lc.shutdown(i,false); // Enable display
    lc.setIntensity(i,15); // Set brightness level (0 is min, 15 is max)
    lc.clearDisplay(i);
  }
  
  joys.reserve(2);
  buttons.reserve(20);
  indicators.reserve(20);
  locks.reserve(2);
  /*
  bargraphs.reserve(5);
  displays.reserve(5);
  */
  
  // Load joysticks into vector
  joys.push_back(Joy("J0", A0, A1, A2, A3));
  joys.push_back(Joy("J1", A4, A5, A6, A7));
  
  // Load buttons into vectors
  /*
  buttons.push_back(Pin("Action 1", "action_group_1", 22, DIGITAL, INPUT_PULLUP));
  buttons.push_back(Pin("Action 2", "action_group_2", 24, DIGITAL, INPUT_PULLUP));
  buttons.push_back(Pin("Action 3", "action_group_3", 26, DIGITAL, INPUT_PULLUP));
  buttons.push_back(Pin("Action 4", "action_group_4", 28, DIGITAL, INPUT_PULLUP));
  buttons.push_back(Pin("Action 5", "action_group_5", 30, DIGITAL, INPUT_PULLUP));
  buttons.push_back(Pin("Action 6", "action_group_6", 32, DIGITAL, INPUT_PULLUP));
  buttons.push_back(Pin("Action 7", "action_group_7", 34, DIGITAL, INPUT_PULLUP));
  buttons.push_back(Pin("Action 8", "action_group_8", 36, DIGITAL, INPUT_PULLUP));
  buttons.push_back(Pin("Action 9", "action_group_9", 38, DIGITAL, INPUT_PULLUP));
  buttons.push_back(Pin("Action 10", "action_group_10", 40, DIGITAL, INPUT_PULLUP));
  
  buttons.push_back(Pin("Gear", "gear", 14, DIGITAL, INPUT_PULLUP));
  indicators.push_back(Pin("Gear Status", "action_group_light", 0, DIGITAL, OUTPUT));
  
  buttons.push_back(Pin("Brakes", "brake", 15, DIGITAL, INPUT_PULLUP));
  indicators.push_back(Pin("Brakes Status", "action_group_brake", 1, DIGITAL, OUTPUT));
  
  buttons.push_back(Pin("Lights", "light", 16, DIGITAL, INPUT_PULLUP));
  indicators.push_back(Pin("Lights Status", "action_group_light", 2, DIGITAL, OUTPUT));
  
  buttons.push_back(Pin("RCS", "rcs", 17, DIGITAL, INPUT_PULLUP));
  indicators.push_back(Pin("RCS Status", "rcs_status", 3, DIGITAL, OUTPUT));
  
  buttons.push_back(Pin("SAS", "sas", 18, DIGITAL, INPUT_PULLUP));
  indicators.push_back(Pin("SAS Status", "sas_status", 4, DIGITAL, OUTPUT));
  
  buttons.push_back(Pin("Map", "toggle_map", 19, DIGITAL, INPUT_PULLUP));
  */
  
  // Load locked inputs into vector
  locks.push_back(LockedInput("Stage", "stage", 2, 3, 4, "True"));
  locks.push_back(LockedInput("Abort", "abort", 14, 15, 16, "True"));
  
  /*
  displays.push_back(Display("Ap", "vessel_apoapsis", lc, 8, 1));
  displays.push_back(Display("Pe", "vessel_periapsis", lc, 8, 2));
  displays.push_back(Display("Alt", "vessel_altitude", lc, 8, 3));
  displays.push_back(Display("Vel", "vessel_velocity", lc, 8, 4));
  displays.push_back(Display("Rad", "vessel_asl_height", lc, 4, 5, 0, 3, " "));
  displays.push_back(Display("Inc", "vessel_inclination", lc, 4, 5, 4, 3, " "));
  */
  // Start the serial connection
  Serial.begin(9600);
  // Report online status
  Serial.println("ONLINE");
  // Receive configuration
  // configure();

  // Report calibration status
  Serial.println("CALIBRATING");

  // Calibrate until the staging button is pressed
  calibrate.indicator.set(HIGH);
  
  for (joy=joys.begin(); joy!=joys.end(); joy++) {
    joy->recalibrate();
  }

  while (calibrate.button.get() == LOW) {
    calibrate.button.update();
      
    for(joy=joys.begin(); joy!=joys.end(); joy++) {
      joy->calibrate();
      Serial.println(joy->toString());
    }
    delay(1000);
  }
  calibrate.indicator.set(LOW);
  
  
  // Report ready status
  Serial.println("READY");
}

void configure() {
  StaticJsonBuffer<512> jsonBuffer;
  char* json; // = readLine.c_str();

  // Parse JSON
  JsonObject& configuration = jsonBuffer.parseObject(json);
  if (!configuration.success()) {
    Serial.println("JSON Parsing failed.");
    reset();
  }
}

String processInput() {
  StaticJsonBuffer<512> jsonBuffer;
  JsonObject& input = jsonBuffer.createObject();
  String yaw, pitch, roll, x, y, z, sixdof, tmp;
  
  // Poll all configured hardware 
  for (joy=joys.begin(); joy!=joys.end(); joy++) {
    joy->update();
  }
  
  for (button=buttons.begin(); button!=buttons.end(); button++) {
    button->update();
  }
   
  for (lock=locks.begin(); lock!=locks.end(); lock++) {
    lock->update();
  }
  
  // Aggregate fly-by-wire data
  for (joy=joys.begin(); joy!=joys.end(); joy++) {
    if (joy->name == "J0") {
      yaw = String(joy->X);
      pitch = String(joy->Y);
      roll = String(joy->Z);
    } else if (joy->name == "J1") {
      x = String(joy->X);
      y = String(joy->Y);
      z = String(joy->Z);
    }
  }
//  sixdof=yaw + "," + pitch + "," + roll + "," + x + "," + y + "," + z;
//  input["toggle_fbw"] = "1";
//  input["six_dof"] = sixdof.c_str();

  for (button=buttons.begin(); button!=buttons.end(); button++) { 
    if (button->updated()) {
      tmp = button->toString();
      if (tmp != "") {
        input[button->api.c_str()] = tmp.c_str();
      }
    }
  }
  
  for (lock=locks.begin(); lock!=locks.end(); lock++) {
    if (lock->updated()) {
      tmp = lock->toString();
      if (tmp != "") {
        input[lock->api.c_str()] = tmp.c_str();
      }
    }
  }
  
  // Strip unwanted variable
  input.remove("?");
  
  // Send fly-by-wire data
  input.printTo(Serial);
  Serial.println("");
  
  char buffer[256];
  input.printTo(buffer, sizeof(buffer));
  return buffer;
}

void processOutput(String _output) {
  StaticJsonBuffer<512> jsonBuffer;
  char* json = new char[_output.length() + 1];
  strcpy(json, _output.c_str());

  // Parse received telemetry
  JsonObject& output = jsonBuffer.parseObject(json);
  if (!output.success()) {
    Serial.println("JSON Parsing failed.");
    reset();
  }
  
  for (indicator=indicators.begin(); indicator!=indicators.end(); indicator++) {
    indicator->update();
  }

  // Update instrumentation panels
  /*
  for (bargraph=bargraphs.begin(); bargraph!=bargraphs.end(); bargraph++) {
    bargraph.set(??);
  }
  */ /*
  for (display=displays.begin(); display!=displays.end(); display++) {
    display->set("1234.5678");
  }
  */
}

String sync(String output) {
  String input = "";
  if (output != "") {
    // Wait for telemetry data
    processOutput(output);
    // Send fly-by-wire data
    input = processInput();
  }
  return input; 
}

void loop() {
  delay(1000);
  String input;
  
  /*
  //Serial.println(readLine);
  if (readLine != "") {
    input = sync(readLine);
    Serial.println(input);
  }
  */
  
  processInput();            // Remove this once we have a successful read
  
}


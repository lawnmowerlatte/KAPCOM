#define ANALOG 1
#define DIGITAL 0
#define NULL 0

#include <iterator>
#include <vector>
#include <pnew.cpp>

#include <LedControl.h>
#include <Wire.h>
#include <Adafruit_LEDBackpack.h>
#include <Adafruit_GFX.h>
#include <ArduinoJson.h>

#include <pin.h>
#include <lockedinput.h>
#include <joy.h>
#include <display.h>
#include <bargraph.h>

using namespace std;

// Global Serial Reading
String readLine = "";
String nextLine = "";

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

vector<Bargraph> bargraphs;
vector<Bargraph>::iterator bargraph;

vector<Display> displays;
vector<Display>::iterator display;

void(* reset) (void) = 0;

void serialEvent() {
  String input;

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

  if (readLine != "") {
    if (readLine == "{}") {
      // Retransmission request
      input = processInput();
    } 
    else {
      // Full sync
      input = sync(readLine);
      readLine = "";
    }
    Serial.println(input);
  }
}

void setup() {
  // Start the serial connection
  Serial.begin(115200);
  // Report online status
  Serial.println("ONLINE");
  // Receive configuration
  // configure();

  // Report calibration status
  Serial.println("CALIBRATING");

  // Initialize displays
  for(int i=0; i<display_count; i++) {
    lc.shutdown(i,false); // Enable display
    lc.setIntensity(i,15); // Set brightness level (0 is min, 15 is max)
    lc.clearDisplay(i);
  }

  joys.reserve(2);
  buttons.reserve(23);
  indicators.reserve(20);
  locks.reserve(2);
  bargraphs.reserve(5);
  displays.reserve(5);

  // Load joysticks into vector
  joys.push_back(Joy("J0", A0, A1, A2, A3, false, true, false));
  joys.push_back(Joy("J1", A4, A5, A6, A7, false, false, true));

  // Load buttons into vectors
  buttons.push_back(Pin("Throttle", "set_throttle", A8, ANALOG, INPUT_PULLUP, "Percent"));
  
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
  
  buttons.push_back(Pin("KEY: Ship +", "]", 0, DIGITAL, INPUT_PULLUP));
  buttons.push_back(Pin("KEY: Ship -", "[", 0, DIGITAL, INPUT_PULLUP));
  
  buttons.push_back(Pin("KEY: Warp +", ".", 0, DIGITAL, INPUT_PULLUP));
  buttons.push_back(Pin("KEY: Warp -", ",", 0, DIGITAL, INPUT_PULLUP));
  
  buttons.push_back(Pin("KEY: Quicksave", "F5", 0, DIGITAL, INPUT_PULLUP));
  buttons.push_back(Pin("KEY: Quickload", "F9", 0, DIGITAL, INPUT_PULLUP));
  
  // Load locked inputs into vector
  locks.push_back(LockedInput("Stage", "stage", 2, 3, 4, "True"));
  locks.push_back(LockedInput("Abort", "abort", 14, 15, 16, "True"));

  displays.push_back(Display("Ap", "vessel_apoapsis", lc, 8, 1));
  displays.push_back(Display("Pe", "vessel_periapsis", lc, 8, 2));
  displays.push_back(Display("Alt", "vessel_altitude", lc, 8, 3));
  displays.push_back(Display("Vel", "vessel_velocity", lc, 8, 4));
  displays.push_back(Display("Rad", "vessel_asl_height", lc, 4, 5, 0, 3, " "));
  displays.push_back(Display("Inc", "vessel_inclination", lc, 4, 5, 4, 3, " "));

  bargraphs.push_back(Bargraph("LF", "resource_lf_current", 0));
  bargraphs.push_back(Bargraph("OX", "resource_ox_current", 1));
  bargraphs.push_back(Bargraph("MP", "resource_mp_current", 2));
  bargraphs.push_back(Bargraph("EL", "resource_ec_current", 3));
  bargraphs.push_back(Bargraph("SF", "resource_sf_current", 4));

  // Report ready status
  Serial.println("READY");
}

void configure() {
  StaticJsonBuffer<1024> jsonBuffer;
  char* json; // = readLine.c_str();

  // Parse JSON
  JsonObject& configuration = jsonBuffer.parseObject(json);
  if (!configuration.success()) {
    Serial.println("JSON Parsing failed.");
    delay(1000);
    Serial.println("");
    reset();
  }

  free(json);
}

String processInput() {
  String yaw, pitch, roll, x, y, z, sixdof, tmp;
  bool isSAS=false;

  String q="\"";
  String json="{" +q+ "v" +q+":"+q+ "0.9.0" +q;

  // Poll all configured hardware 
  for (button=buttons.begin(); button!=buttons.end(); button++) {
    button->update();
  }

  for (lock=locks.begin(); lock!=locks.end(); lock++) {
    lock->update();
  }

  // Check SAS: If enabled, remove joystick inputs
  for (indicator=indicators.begin(); indicator!=indicators.end(); indicator++) {
    if (indicator->name == "SAS Status" && indicator->value == 1) {
      isSAS = true;
    }
  }

  if (!isSAS) {
    // Aggregate fly-by-wire data
    for (joy=joys.begin(); joy!=joys.end(); joy++) {
      joy->update();
      if (joy->name == "J0") {
        pitch = String(joy->X);
        yaw = String(joy->Y);
        roll = String(joy->Z);
      } else if (joy->name == "J1") {
        x = String(joy->X);
        y = String(joy->Y);
        z = String(joy->Z);
      }
    }
    sixdof=yaw + "," + pitch + "," + roll + "," + x + "," + y + "," + z;
    json+=","+q+ "toggle_fbw" +q+":"+q+ "1" +q;
    json+=","+q+ "six_dof" +q+":"+q+ sixdof +q;
  }

  // Aggregate button inputs
  for (lock=locks.begin(); lock!=locks.end(); lock++) {
    if (lock->changed()) {
      tmp = lock->toString();
      if (tmp != "") {
        json+=","+q+ lock->api +q+":"+q+ lock->toString() +q;
      }
    }
  }

  for (button=buttons.begin(); button!=buttons.end(); button++) { 
    if (button->changed()) {
      tmp = button->toString();
      if (tmp != "") {
        json+=","+q+ button->api +q+":"+q+ button->toString() +q;
      }
    }
  }

  json += "}";
  return json;
}

void processOutput(String _output) {
  StaticJsonBuffer<1024> jsonBuffer;
  char* json = new char[_output.length() + 1];
  strcpy(json, _output.c_str());

  // Parse received telemetry
  JsonObject& output = jsonBuffer.parseObject(json);
  if (!output.success()) {
    Serial.println("JSON Parsing failed.");
    delay(1000);
    Serial.println("");
    reset();
  }

  char* api = new char[20];
  char* value = new char[20];

  for (indicator=indicators.begin(); indicator!=indicators.end(); indicator++) {
    strcpy(api, indicator->api.c_str());
    strcpy(value, output[api]);
    if (value[0] > 0) {
      indicator->set(value);
    }
  }

  // Update instrumentation panels
  for (bargraph=bargraphs.begin(); bargraph!=bargraphs.end(); bargraph++) {
    strcpy(api, indicator->api.c_str());
    strcpy(value, output[api]);
    if (value[0] > 0) {
      bargraph->set(value);
    }
  }
  
  for (display=displays.begin(); display!=displays.end(); display++) {
    strcpy(api, indicator->api.c_str());
    strcpy(value, output[api]);
    if (value[0] > 0) {
      display->set(value);
    }
  }
  
  free(json);
  free(api);
  free(value);
}

String sync(String output) {
  String input;
  if (output != "") {
    // Wait for telemetry data
    processOutput(output);
    // Send fly-by-wire data
    input = processInput();
  }
  return input; 
}

void loop() { }

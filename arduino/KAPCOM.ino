#define ANALOG 1
#define DIGITAL 0
#define NULL 0

#include <MemoryFree.h>
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
String readLine;
String nextLine;

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
  while (Serial.available()) {
    char c = (char)Serial.read();

    if (c == '\n' || c == 10 || c == 13) {
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

void setup() {
  
  // Start the serial connection
  Serial.begin(115200);
  
  Serial.println(freeMemory());
  readLine.reserve(100);
  nextLine.reserve(100);
  Serial.println(freeMemory());
  
  
  // Report online status
  Serial.println(F("ONLINE"));
  // Receive configuration
  // configure();

  // Report calibration status
  Serial.println(F("CALIBRATING"));

  Pin p = Pin(F("Throttle"), F("set_throttle"), A8, ANALOG, INPUT_PULLUP, F("Percent"));

//  Serial.println(freeMemory());
//  initVectors();
//  showVectors();
//  Serial.println(freeMemory());
//  initJoysticks();
//  Serial.println(freeMemory());
//  initInputs();
//  Serial.println(freeMemory());
//  initCombos();
//  Serial.println(freeMemory());
//  initLocks();
//  Serial.println(freeMemory());
//  initDisplays();
//  Serial.println(freeMemory());
//  initBargraphs();
  Serial.println(freeMemory());

//  showVectors();
  
  // Report ready status
  Serial.println(F("READY"));
}
  
void showVectors() {
  Serial.println(joys.size());
  Serial.println(buttons.size());
  Serial.println(indicators.size());
  Serial.println(locks.size());
  Serial.println(displays.size());
  Serial.println(bargraphs.size());
}
  
void initVectors() {
//  Serial.print(F("Reserving vectors: "));
//  Serial.print(freeMemory());
  joys.reserve(2);
  buttons.reserve(23);
  indicators.reserve(5);
  locks.reserve(2);
  bargraphs.reserve(5);
  displays.reserve(6);
//  Serial.print(", ");
//  Serial.println(freeMemory());
}

void initJoysticks() {
//  Serial.print(F("Adding Joysticks: "));
//  Serial.print(freeMemory());
  // Load joysticks into vector
  joys.push_back(Joy(F("J0"), A0, A1, A2, A3, false, true, false));
  joys.push_back(Joy(F("J1"), A4, A5, A6, A7, false, false, true));
//  Serial.print(F(", "));
//  Serial.println(freeMemory());
}
  
void initInputs() {
//  Serial.print(F("Adding inputs: "));
//  Serial.print(freeMemory());
  
  // Load buttons into vectors
  buttons.push_back(Pin(F("Throttle"), F("set_throttle"), A8, ANALOG, INPUT_PULLUP, F("Percent")));
  
  buttons.push_back(Pin(F("Action 1"), F("action_group_1"), 22, DIGITAL, INPUT_PULLUP));
  buttons.push_back(Pin(F("Action 2"), F("action_group_2"), 24, DIGITAL, INPUT_PULLUP));
  buttons.push_back(Pin(F("Action 3"), F("action_group_3"), 26, DIGITAL, INPUT_PULLUP));
  buttons.push_back(Pin(F("Action 4"), F("action_group_4"), 28, DIGITAL, INPUT_PULLUP));
  buttons.push_back(Pin(F("Action 5"), F("action_group_5"), 30, DIGITAL, INPUT_PULLUP));
  buttons.push_back(Pin(F("Action 6"), F("action_group_6"), 32, DIGITAL, INPUT_PULLUP));
  buttons.push_back(Pin(F("Action 7"), F("action_group_7"), 34, DIGITAL, INPUT_PULLUP));
  buttons.push_back(Pin(F("Action 8"), F("action_group_8"), 36, DIGITAL, INPUT_PULLUP));
  buttons.push_back(Pin(F("Action 9"), F("action_group_9"), 38, DIGITAL, INPUT_PULLUP));
  buttons.push_back(Pin(F("Action 10"), F("action_group_10"), 40, DIGITAL, INPUT_PULLUP));
  
  buttons.push_back(Pin(F("Map"), F("toggle_map"), 33, DIGITAL, INPUT_PULLUP));
  
  buttons.push_back(Pin(F("KEY: Ship +"), F("]"), 34, DIGITAL, INPUT_PULLUP));
  buttons.push_back(Pin(F("KEY: Ship -"), F("["), 35, DIGITAL, INPUT_PULLUP));
  
  buttons.push_back(Pin(F("KEY: Warp +"), F("."), 36, DIGITAL, INPUT_PULLUP));
  buttons.push_back(Pin(F("KEY: Warp -"), F(","), 37, DIGITAL, INPUT_PULLUP));
  
  buttons.push_back(Pin(F("KEY: Quicksave"), F("F5"), 38, DIGITAL, INPUT_PULLUP));
  buttons.push_back(Pin(F("KEY: Quickload"), F("F9"), 39, DIGITAL, INPUT_PULLUP));
//  Serial.print(F(", "));
//  Serial.println(freeMemory());
}

void initCombos() {
//  Serial.print(F("Adding combos: "));
//  Serial.print(freeMemory());
  
  buttons.push_back(Pin(F("Gear"), F("gear"), 23, DIGITAL, INPUT_PULLUP));
  indicators.push_back(Pin(F("Gear Status"), F("action_group_light"), 24, DIGITAL, OUTPUT));
   
  buttons.push_back(Pin(F("Brakes"), F("brake"), 25, DIGITAL, INPUT_PULLUP));
  indicators.push_back(Pin(F("Brakes Status"), F("action_group_brake"), 26, DIGITAL, OUTPUT));
   
  buttons.push_back(Pin(F("Lights"), F("light"), 27, DIGITAL, INPUT_PULLUP));
  indicators.push_back(Pin(F("Lights Status"), F("action_group_light"), 28, DIGITAL, OUTPUT));
   
  buttons.push_back(Pin(F("RCS"), F("rcs"), 29, DIGITAL, INPUT_PULLUP));
  indicators.push_back(Pin(F("RCS Status"), F("rcs_status"), 30, DIGITAL, OUTPUT));
   
  buttons.push_back(Pin(F("SAS"), F("sas"), 31, DIGITAL, INPUT_PULLUP));
  indicators.push_back(Pin(F("SAS Status"), F("sas_status"), 32, DIGITAL, OUTPUT));
//  Serial.print(F(", "));
//  Serial.println(freeMemory());
}
 
void initLocks() { 
//  Serial.print(F("Adding locked inputs: "));
//  Serial.print(freeMemory());
  // Load locked inputs into vector
  locks.push_back(LockedInput(F("Stage"), F("stage"), A9, A10, A11, F("True")));
  locks.push_back(LockedInput(F("Abort"), F("abort"), A12, A13, A14, F("True")));
//  Serial.print(F(", "));
//  Serial.println(freeMemory());
}

void initDisplays() {
//  Serial.print(F("Adding displays: "));
//  Serial.print(freeMemory());
  
  // Initialize displays
  for(int i=0; i<display_count; i++) {
    lc.shutdown(i,false); // Enable display
    lc.setIntensity(i,15); // Set brightness level (0 is min, 15 is max)
    lc.clearDisplay(i);
  }
  
  displays.push_back(Display(F("Ap"), F("vessel_apoapsis"), lc, 8, 1));
  displays.push_back(Display(F("Pe"), F("vessel_periapsis"), lc, 8, 2));
  displays.push_back(Display(F("Alt"), F("vessel_altitude"), lc, 8, 3));
  displays.push_back(Display(F("Vel"), F("vessel_velocity"), lc, 8, 4));
  displays.push_back(Display(F("Rad"), F("vessel_asl_height"), lc, 4, 5, 0, 3, " "));
  displays.push_back(Display(F("Inc"), F("vessel_inclination"), lc, 4, 5, 4, 3, " "));
//  Serial.print(F(", "));
//  Serial.println(freeMemory());
} 
 
void initBargraphs() { 
//  Serial.print(F("Adding bargraphs: "));
//  Serial.print(freeMemory());
  bargraphs.push_back(Bargraph(F("LF"), F("resource_lf_current"), 0));
  bargraphs.push_back(Bargraph(F("OX"), F("resource_ox_current"), 1));
  bargraphs.push_back(Bargraph(F("MP"), F("resource_mp_current"), 2));
  bargraphs.push_back(Bargraph(F("EL"), F("resource_ec_current"), 3));
  bargraphs.push_back(Bargraph(F("SF"), F("resource_sf_current"), 4));
//  Serial.print(F(", "));
//  Serial.println(freeMemory());
}

void configure() {
  StaticJsonBuffer<1024> jsonBuffer;
  char* json; // = readLine.c_str();

  // Parse JSON
  JsonObject& configuration = jsonBuffer.parseObject(json);
  if (!configuration.success()) {
    Serial.println(F("JSON Parsing failed."));
    delay(1000);
    Serial.println(F(""));
    reset();
  }

  free(json);
}

String processInput() {
  String yaw, pitch, roll, x, y, z, sixdof, tmp;
  bool isSAS=false;
  String comma=F(",");
  String colon=F(":");
  String q=F("\"");

  String json=F("{\"v\":\"0.9.0\"");

  // Poll all configured hardware 
  for (button=buttons.begin(); button!=buttons.end(); button++) {
    button->update();
  }

  for (lock=locks.begin(); lock!=locks.end(); lock++) {
    lock->update();
  }

  // Check SAS: If enabled, remove joystick inputs
  for (indicator=indicators.begin(); indicator!=indicators.end(); indicator++) {
    if (indicator->name == F("SAS Status") && indicator->value == 1) {
      isSAS = true;
    }
  }

  if (!isSAS) {
    // Aggregate fly-by-wire data
    for (joy=joys.begin(); joy!=joys.end(); joy++) {
      joy->update();
      if (joy->name == F("J0")) {
        pitch = String(joy->X);
        yaw = String(joy->Y);
        roll = String(joy->Z);
      } else if (joy->name == F("J1")) {
        x = String(joy->X);
        y = String(joy->Y);
        z = String(joy->Z);
      }
    }

    sixdof=yaw +comma + pitch + comma + roll + comma + x + comma + y + comma + z;
    json+=comma+q+ F("toggle_fbw") +q+colon+q+ F("1") +q;
    json+=comma+q+ F("six_dof") +q+colon+q+ sixdof +q;
  }

  // Aggregate button inputs
  for (lock=locks.begin(); lock!=locks.end(); lock++) {
    if (lock->changed()) {
      tmp = lock->toString();
      if (tmp != F("")) {
        json+=comma+q+ lock->api +q+colon+q+ lock->toString() +q;
      }
    }
  }

  for (button=buttons.begin(); button!=buttons.end(); button++) { 
    if (button->changed()) {
      tmp = button->toString();
      if (tmp != F("")) {
        json+=comma+q+ button->api +q+colon+q+ button->toString() +q;
      }
    }
  }

  json += F("}");
  return json;
}

void processOutput(char* json) {
  Serial.println("processOutput: 1: " + String(freeMemory()));
  StaticJsonBuffer<1024> jsonBuffer;
//  char* json = new char[_output.length() + 1];
//  strcpy(json, _output.c_str());
  Serial.println("processOutput: 2: " + String(freeMemory()));
  // Parse received telemetry
  JsonObject& output = jsonBuffer.parseObject(json);
  if (!output.success()) {
    Serial.print(F("JSON Parsing failed: "));
//    Serial.println(_output);
    delay(1000);
    Serial.println("");
    reset();
  }
  Serial.println("processOutput: 3: " + String(freeMemory()));
  char* api = new char[20];
  char* value = new char[20];
  Serial.println("processOutput: 4: " + String(freeMemory()));

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
  
//  free(json);
  free(api);
  free(value);
  Serial.println("processOutput: 5: " + String(freeMemory()));
}

String sync(char* output) {
  Serial.println("sync: 1: " + String(freeMemory()));
  if (*output != '\0') {
    // Wait for telemetry data
    processOutput(output);
    // Send fly-by-wire data
    Serial.println("sync: 2: " + String(freeMemory()));
    return processInput();
  }
  return F(""); 
}

void loop() {
  if (readLine != F("")) {
    Serial.print(freeMemory());
    Serial.print(": ");

    if (readLine == F("{}")) {
      // Retransmission request
      Serial.print("RETRANSMIT: ");
      Serial.print(readLine);
      Serial.print(": ");
      Serial.println(processInput());
    } 
    else {
      // Full sync
    Serial.println(sync((char *)readLine.c_str()));
    }
    
    readLine = F("");
  }
}

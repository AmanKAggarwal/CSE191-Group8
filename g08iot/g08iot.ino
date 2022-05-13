/*
  Group 08

*/

// Global includes
#include <ArduinoJson.h>

// wifi comms includes
#include <WiFi.h>
#include <HTTPClient.h>


// local includes

// check device MAC table to get wifi password
#define MAN_SSID "3840WiFi"
#define MAN_PSWD "LoudShark480"  

// --------------------------------------------------------------------


// --------------------------------------------------------------------

static volatile bool wifiConnected = false;
String localSSID, localPSWD;
String regURL;
String postStr;

static volatile bool tog = false;
static volatile int userCount = 0;


// -------------------------------------------------------



/*********************** SETUP ******************************/
void setup(){

  // configure the i/o
  Serial.begin(115200);

  delay(50);
  Serial.println("CSE191 IoT Web call example");
  
  WiFi.onEvent(WiFiEvent);
  WiFi.mode(WIFI_MODE_STA);

  scanWiFiNetworks();

  localSSID = MAN_SSID;
  localPSWD = MAN_PSWD;
  
  // setup STA mode
  WiFi.mode(WIFI_MODE_STA);
  Serial.println("Trying SSID: " + localSSID + " (" + localPSWD + ")");

  delay(50);
  // connect to the local wifi
  WiFi.begin(localSSID.c_str(), localPSWD.c_str());

  // show MAC address
  Serial.println();
  Serial.println("my MAC:"+getMacStr());

  // wait till we are connected
  while (!wifiConnected)
      ; 
      
  getGeoLocation();
}

// ------------------------------ MAIN LOOP --------------------------------
void loop(){

/* From last LAB ../apixx/logdevices?gn=<groupname>&mac=<mac address>&rssi=<rssi value> */

  regURL = "http://cse191.ucsd.edu/api08/logdevices?gn=Innovators&mac="+getMacStr()+"&rssi="+WiFi.RSSI();
  String locStr = getGeoLocation();
  if (locStr != "") {
    regURL += "&" + locStr + "&color=blue";
  }
  getHTTP(regURL);

  //postStr = "{\"field\": \"value\", \"other\": \"45\"}";
  //postJsonHTTP(regURL, postStr);

  delay(10000);

}

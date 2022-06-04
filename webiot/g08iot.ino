/*
  Group 08

*/

// Global includes
#include <ArduinoJson.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>


// wifi comms includes
#include <WiFi.h>
#include <HTTPClient.h>


// local includes

// check device MAC table to get wifi password

#define MAN_SSID "UCSD-DEVICE"
#define MAN_PSWD "Fj7UPsFHb84e"  

// --------------------------------------------------------------------


// --------------------------------------------------------------------

static volatile bool wifiConnected = false;
String localSSID, localPSWD;
String logBeaconsURL;
String logDeviceURL;
String postStr;

static volatile bool tog = false;
static volatile int userCount = 0;


// -------------------------------------------------------


int scanTime = 1; //In seconds
BLEScan* pBLEScan;
String becaonStrList = "";
char buf[2000];

StaticJsonDocument<4000> jBLEList;
// create an empty array
JsonArray bleArray = jBLEList.to<JsonArray>();

String  parseBeacon(BLEAdvertisedDevice dev) {

      // vars used in building json object
      StaticJsonDocument<400> jBLEDoc;
      char jChar[800] = "";

      // clear the json object
      jBLEDoc.clear();
      
      jBLEDoc["mac"] = String(dev.getAddress().toString().c_str());   // get the beacon mac addr
      jBLEDoc["rssi"] = String(dev.getRSSI());                        // record rssi power
     

      serializeJson(jBLEDoc, jChar);                                  // convert to string
      //Serial.printf("BLE JSON (%d): %s\n",jBLEDoc.memoryUsage(),jChar);
      
      if (becaonStrList.length() > 0)
        becaonStrList = becaonStrList + "," + String(jChar);
      else
        becaonStrList = becaonStrList + String(jChar);
      
      return String(jChar);
}


class MyAdvertisedDeviceCallbacks: public BLEAdvertisedDeviceCallbacks {
    void onResult(BLEAdvertisedDevice advertisedDevice) {
      Serial.printf("Advertised Device: %s \n", advertisedDevice.toString().c_str());
      parseBeacon(advertisedDevice);
    }
};


/*********************** SETUP ******************************/
void setup(){

  // configure the i/o
  Serial.begin(115200);

  delay(50);
  Serial.println("CSE191 IoT Web call example");
  Serial.println("CSE 191 Scanning Example");

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
      
//  getGeoLocation();
  BLEDevice::init("");
  pBLEScan = BLEDevice::getScan(); //create new scan
  pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
  pBLEScan->setActiveScan(true); //active scan uses more power, but get results faster
  pBLEScan->setInterval(100);
  pBLEScan->setWindow(99);  // less or equal setInterval value
}

// ------------------------------ MAIN LOOP --------------------------------
void loop(){

/* From last LAB ../apixx/logdevices?gn=<groupname>&mac=<mac address>&rssi=<rssi value> */

  logDeviceURL = "http://cse191.ucsd.edu/api08/logdevices?gn=Innovators&mac="+getMacStr()+"&rssi="+WiFi.RSSI();

  Serial.println(logDeviceURL);
  getHTTP(logDeviceURL);

  becaonStrList = "";
  BLEScanResults foundDevices = pBLEScan->start(scanTime, false);
  Serial.print("Devices found: ");
  Serial.println(foundDevices.getCount());
  Serial.println("Scan done!");
  becaonStrList = "{\"groupname\":\"Innovators\", \"dev_mac\":\""+getMacStr()+"\", \"dev_rssi\":\""+WiFi.RSSI()+"\", \"beacons\":[" + becaonStrList + "]}";
  becaonStrList.toCharArray(buf, sizeof(buf));
//  Serial.printf("BLE List: %s\n",buf);
  pBLEScan->clearResults();   // delete results fromBLEScan buffer to release memory

  logBeaconsURL = "http://cse191.ucsd.edu/api08/logBeacons";
  postJsonHTTP(logBeaconsURL, becaonStrList);
  Serial.println("Beacons sent");

  delay(10000);

}
#include <ArduinoBLE.h>
#include "DHT.h"

// Pins
#define DHTPIN 2
#define DHTTYPE DHT11
#define BUZZER 9
#define RED 10
#define GREEN 11
#define BLUE 12

// BLE UUIDs
const char* SERVICE_UUID       = "f75cfb20-4bce-4d2a-a9a7-3d9a93e0e2f5";
const char* SENSOR_CHAR_UUID   = "f75cfb21-4bce-4d2a-a9a7-3d9a93e0e2f5";
const char* COMMAND_CHAR_UUID  = "f75cfb22-4bce-4d2a-a9a7-3d9a93e0e2f5";

DHT dht(DHTPIN, DHTTYPE);
BLEService sensorService(SERVICE_UUID);
BLEStringCharacteristic sensorChar(SENSOR_CHAR_UUID, BLERead | BLENotify, 64); //send sensor data
BLEStringCharacteristic commandChar(COMMAND_CHAR_UUID, BLEWrite, 32);   //receive control commands
 
unsigned long lastSend = 0;   //last time send data timesamp
const unsigned long sendInterval = 3000; // 3 seconds

void setup() {   //only one time init when start
  Serial.begin(9600);
  dht.begin();

  pinMode(BUZZER, OUTPUT);
  pinMode(RED, OUTPUT);
  pinMode(GREEN, OUTPUT);
  pinMode(BLUE, OUTPUT);

  noTone(BUZZER);
  setRGB(0, 1, 0); // default green

  if (!BLE.begin()) {
    Serial.println("BLE init failed, check hardware!");
    while (1);
  }

  BLE.setLocalName("cc123"); // must match python BLE_NAME
  BLE.setAdvertisedService(sensorService);
  sensorService.addCharacteristic(sensorChar);
  sensorService.addCharacteristic(commandChar);
  BLE.addService(sensorService);
  BLE.advertise();

  Serial.println("BLE Ready (waiting for bridge)...");
}

void loop() {
  BLE.poll();  //  ensure BLE stays active

  BLEDevice central = BLE.central();
  if (!central) {
    // Keep advertising if no connection
    BLE.advertise();
  }

  // Always collect sensor data
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  if (!isnan(h) && !isnan(t)) {  //if it does work ，status will show normal
    String status = "NORMAL";
    if (t < 19 || h > 70) {   //
      status = "ALERT";
      setRGB(1, 0, 0);
      tone(BUZZER, 1000);  //buzzer bb
      delay(500);
      noTone(BUZZER);  //no bb
    } else {
      setRGB(0, 1, 0);  //another situation green no bb 
      noTone(BUZZER);
    }

    Serial.print("Temp: ");
    Serial.print(t);
    Serial.print(" °C, Hum: ");
    Serial.print(h);
    Serial.print(" %, Status: ");
    Serial.println(status);

    // Only send to BLE when connected
    if (central && central.connected()) {
      String payload = String("{\"temperature\":") + t +
                       ",\"humidity\":" + h +
                       ",\"status\":\"" + status + "\"}";
      sensorChar.writeValue(payload);
    }
  } else {
    Serial.println("DHT11 read error!"); //failed
  }

  //  commands
  if (commandChar.written()) {
    String cmd = commandChar.value();  //read command char
    cmd.trim();   //delete sapce
    cmd.toLowerCase();   // 小写lowcase

    Serial.print("BLE command: ");
    Serial.println(cmd);

    if (cmd == "{\"led\":\"on\"}" || cmd == "on") {
      setRGB(1, 0, 0);
      tone(BUZZER, 1000);
      delay(3000);
      noTone(BUZZER);
    } 
    else if (cmd == "{\"led\":\"off\"}" || cmd == "off") {
      setRGB(0, 1, 0);
      noTone(BUZZER);
    }
  }

  delay(1000);
}

void setRGB(int r, int g, int b) {
  digitalWrite(RED, r ? HIGH : LOW); //r为1 红亮
  digitalWrite(GREEN, g ? HIGH : LOW);  //g为1 绿亮
  digitalWrite(BLUE, b ? HIGH : LOW); //没用这个
}

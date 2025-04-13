#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "config.h"

// Pin definitions
const int SOIL_MOISTURE_PIN = 34;  // Analog pin for soil moisture sensor
const int SOLENOID_VALVE_PIN = 26; // Digital pin for solenoid valve control

// Variables
int soilMoistureValue = 0;
int soilMoisturePercent = 0;
bool valveStatus = false;
unsigned long lastSendTime = 0;
const unsigned long sendInterval = 10000; // Send data every 10 seconds

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  // Initialize pins
  pinMode(SOIL_MOISTURE_PIN, INPUT);
  pinMode(SOLENOID_VALVE_PIN, OUTPUT);
  digitalWrite(SOLENOID_VALVE_PIN, LOW);  // Ensure valve is off at startup
  
  // Connect to WiFi
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(WIFI_SSID);
  
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  unsigned long currentMillis = millis();
  
  // Read soil moisture sensor
  soilMoistureValue = analogRead(SOIL_MOISTURE_PIN);
  
  // Map the sensor value to a percentage (adjust these values according to your sensor)
  // Assuming 4095 is dry (0%) and 1500 is wet (100%)
  soilMoisturePercent = map(soilMoistureValue, 4095, 1500, 0, 100);
  soilMoisturePercent = constrain(soilMoisturePercent, 0, 100);
  
  // Print readings to serial
  Serial.print("Soil Moisture Value: ");
  Serial.println(soilMoistureValue);
  Serial.print("Soil Moisture Percent: ");
  Serial.println(soilMoisturePercent);
  Serial.print("Valve Status: ");
  Serial.println(valveStatus ? "ON" : "OFF");
  
  // Send data to Raspberry Pi periodically
  if (currentMillis - lastSendTime >= sendInterval) {
    lastSendTime = currentMillis;
    sendDataToServer();
    checkForCommands();
  }
  
  delay(1000);
}

void sendDataToServer() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    
    // Prepare URL
    String url = "http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) + "/sensor-data";
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    
    // Create JSON document
    StaticJsonDocument<200> doc;
    doc["node_id"] = NODE_ID;
    doc["soil_moisture"] = soilMoisturePercent;
    doc["valve_status"] = valveStatus;
    doc["battery"] = 100; // Placeholder for battery level
    
    String requestBody;
    serializeJson(doc, requestBody);
    
    // Send POST request
    int httpResponseCode = http.POST(requestBody);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("HTTP Response code: " + String(httpResponseCode));
      Serial.println(response);
    } else {
      Serial.print("Error on sending data. Error code: ");
      Serial.println(httpResponseCode);
    }
    
    http.end();
  } else {
    Serial.println("WiFi Disconnected");
    // Try to reconnect
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  }
}

void checkForCommands() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    
    // Prepare URL
    String url = "http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) + "/node-command/" + String(NODE_ID);
    http.begin(url);
    
    // Send GET request
    int httpResponseCode = http.GET();
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("HTTP Response code: " + String(httpResponseCode));
      Serial.println(response);
      
      // Parse JSON response
      StaticJsonDocument<200> doc;
      DeserializationError error = deserializeJson(doc, response);
      
      if (!error) {
        // Check for valve command
        if (doc.containsKey("valve_command")) {
          bool command = doc["valve_command"];
          setValveState(command);
        }
      } else {
        Serial.print("deserializeJson() failed: ");
        Serial.println(error.c_str());
      }
    } else {
      Serial.print("Error on receiving command. Error code: ");
      Serial.println(httpResponseCode);
    }
    
    http.end();
  }
}

void setValveState(bool state) {
  valveStatus = state;
  digitalWrite(SOLENOID_VALVE_PIN, state ? HIGH : LOW);
  Serial.print("Valve set to: ");
  Serial.println(state ? "ON" : "OFF");
}
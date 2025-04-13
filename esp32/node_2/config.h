#ifndef CONFIG_H
#define CONFIG_H

// Node identification
#define NODE_ID "node2"  // Unique ID for this node

// WiFi credentials
#define WIFI_SSID "YourWiFiSSID"  // Replace with your WiFi SSID
#define WIFI_PASSWORD "YourWiFiPassword"  // Replace with your WiFi password

// Server configuration
#define SERVER_IP "192.168.1.100"  // Replace with Raspberry Pi IP address
#define SERVER_PORT 5000  // Server port

// Sensor calibration
#define MOISTURE_DRY_VALUE 4095   // ADC value when sensor is completely dry
#define MOISTURE_WET_VALUE 1500   // ADC value when sensor is in water

// Timing configuration
#define READING_INTERVAL 1000     // Time between sensor readings (milliseconds)
#define SEND_INTERVAL 10000       // Time between data transmissions (milliseconds)

#endif // CONFIG_H
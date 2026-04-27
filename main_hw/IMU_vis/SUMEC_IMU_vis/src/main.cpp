#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

#define SDA_PIN 36
#define SCL_PIN 35

Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x29, &Wire); 

void setup() {
  Serial.begin(115200);
  Wire.begin(SDA_PIN, SCL_PIN, 100000); 
  delay(500); 

  if (!bno.begin()) {
    Serial.println("BNO055 not found!");
    while (1);
  }
}

void loop() {
  // Get Quaternions directly from the sensor hardware
  imu::Quaternion quat = bno.getQuat();
  
  // Print in the format expected by the Python parser
  Serial.print("Quat: ");
  Serial.print(quat.w(), 4);
  Serial.print(", ");
  Serial.print(quat.x(), 4);
  Serial.print(", ");
  Serial.print(quat.y(), 4);
  Serial.print(", ");
  Serial.println(quat.z(), 4);

  delay(20); 
}

//cd C:\Users\MenMe\Documents\GitHub\GPS-Compass\_code\Python_IMU_viz
//cd C:\Users\MenMe\GitHub\GPS-Compass\_code\IMU_vis
//cd C:\Users\MenMe\GitHub\GPS-Compass\_code\IMU_vis\Python_IMU_vis

//cd C:\Users\MenMe\Documents\GitHub\Sumec-MiniSumo-HW\main_hw\IMU_vis\Python_IMU_vis
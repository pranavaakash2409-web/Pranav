#include <OneWire.h>
#include <DallasTemperature.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

#define ONE_WIRE_BUS 4
#define CURRENT_PIN 34
#define GAS_PIN 35
#define RELAY_PIN 25
#define BUZZER_PIN 26
#define LED_GREEN 12
#define LED_YELLOW 13
#define LED_RED 14

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature tempSensor(&oneWire);
Adafruit_MPU6050 mpu;

bool simulatedFault = false;

void setup() {
  Serial.begin(115200);
  tempSensor.begin();
  Wire.begin();
  mpu.begin();

  pinMode(RELAY_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_RED, OUTPUT);

  digitalWrite(RELAY_PIN, LOW); // Relay NC closed (normal state)
  digitalWrite(LED_GREEN, HIGH);
}

void loop() {
  // Listen for simulation commands over USB
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "SIMULATE_FAULT") simulatedFault = true;
    if (cmd == "RESET") simulatedFault = false;
  }

  // Read sensors
  tempSensor.requestTemperatures();
  float temp = tempSensor.getTempCByIndex(0);
  
  int rawCurrent = analogRead(CURRENT_PIN);
  float current = (rawCurrent / 4095.0) * 10.0; // Scaled safe current reading
  
  int rawGas = analogRead(GAS_PIN);
  float gas = (rawGas / 4095.0) * 100.0; // Scaled gas/anomaly proxy percentage

  sensors_event_t a, g, mpuTemp;
  mpu.getEvent(&a, &g, &mpuTemp);
  float vib = sqrt(a.acceleration.x * a.acceleration.x + 
                   a.acceleration.y * a.acceleration.y + 
                   a.acceleration.z * a.acceleration.z);

  // Override readings if software fault inject is active
  if (simulatedFault) {
    temp = 82.5; current = 14.2; gas = 75.0; vib = 28.0;
  }

  // Independent Local Hardware Safety Path
  bool unsafe = (temp > 70.0 || current > 10.0 || gas > 60.0 || vib > 22.0);

  if (unsafe) {
    digitalWrite(RELAY_PIN, HIGH);  // Open relay to break load circuit
    digitalWrite(BUZZER_PIN, HIGH); // Sound local alarm
    digitalWrite(LED_RED, HIGH);
    digitalWrite(LED_GREEN, LOW);
  } else {
    digitalWrite(RELAY_PIN, LOW);
    digitalWrite(BUZZER_PIN, LOW);
    digitalWrite(LED_RED, LOW);
    digitalWrite(LED_GREEN, HIGH);
  }

  // Output sensor payload over USB Serial
  Serial.print("{\"temp\":"); Serial.print(temp);
  Serial.print(",\"current\":"); Serial.print(current);
  Serial.print(",\"vib\":"); Serial.print(vib);
  Serial.print(",\"gas\":"); Serial.print(gas);
  Serial.print(",\"unsafe\":"); Serial.print(unsafe ? "true" : "false");
  Serial.println("}");

  delay(1000);
}

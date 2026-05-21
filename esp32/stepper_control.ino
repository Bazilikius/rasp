#include <AccelStepper.h>

// Define motor interface type
// 1 means a stepper driver (Step and Direction pins)
#define motorInterfaceType 1

// Define pin connections
const int stepPin = 12;
const int dirPin = 14;

// Initialize the stepper library
AccelStepper stepper(motorInterfaceType, stepPin, dirPin);

void setup() {
  Serial.begin(115200);

  // Set maximum speed and acceleration
  stepper.setMaxSpeed(1000);
  stepper.setAcceleration(500);

  Serial.println("ESP32 Stepper Control Ready");
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    if (input.startsWith("P")) {
      long targetPosition = input.substring(1).toInt();
      stepper.moveTo(targetPosition);
      Serial.print("Moving to: ");
      Serial.println(targetPosition);
    } else if (input.startsWith("S")) {
      float speed = input.substring(1).toFloat();
      stepper.setMaxSpeed(speed);
      Serial.print("Speed set to: ");
      Serial.println(speed);
    }
  }

  stepper.run();
}

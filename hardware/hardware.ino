// Arduino Nano Every - Actuator Control
// Controls actuator via serial commands and reads ACS712 current sensor

const int IN2 = 2;    // Direction control
const int AN2 = 3;    // Speed control (PWM)
const int CURRENT_SENSOR_PIN = A0;  // Current sensor
const int IN1 = 5;    // Lock actuator direction
const int AN1 = 6;    // Lock actuator speed (PWM)

void setup() {
  pinMode(IN2, OUTPUT);
  pinMode(AN2, OUTPUT);
  pinMode(IN1, OUTPUT);   // Lock actuator
  pinMode(AN1, OUTPUT);   // Lock actuator
  pinMode(CURRENT_SENSOR_PIN, INPUT);
  Serial.begin(115200);
  stopMotor();
  analogWrite(AN1, 0);    // Ensure lock actuator is stopped
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "EXTEND") {
      extend();
      Serial.println("DONE");
    } else if (cmd == "RETRACT") {
      retract();
      Serial.println("DONE");
    } else if (cmd == "STOP") {
      stopMotor();
      Serial.println("DONE");
    } else if (cmd == "LOCK_EXTEND") {
      lockExtend();
      Serial.println("DONE");
    } else if (cmd == "LOCK_RETRACT") {
      lockRetract();
      Serial.println("DONE");
    } else if (cmd == "STOP_LOCK") {
      stopLock();
      Serial.println("DONE");
    } else if (cmd == "READ") {
      int current = analogRead(CURRENT_SENSOR_PIN);
      Serial.print("CURRENT:");
      Serial.println(current);
    }
  }
}

void extend() {
  digitalWrite(IN2, LOW);
  analogWrite(AN2, 255);  // Full speed
}

void retract() {
  digitalWrite(IN2, HIGH);
  analogWrite(AN2, 255);  // Full speed
}

void stopMotor() {
  analogWrite(AN2, 0);  // Stop motor
}

void lockExtend() {
  digitalWrite(IN1, LOW);
  analogWrite(AN1, 255);  // Full speed
}

void lockRetract() {
  digitalWrite(IN1, HIGH);
  analogWrite(AN1, 255);  // Full speed
}

void stopLock() {
  analogWrite(AN1, 0);    // Stop lock actuator
}
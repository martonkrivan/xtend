// Arduino Nano Every - Actuator Control
// Controls actuator via serial commands and reads ACS712 current sensor

const int IN2 = 2;    // Direction control
const int AN2 = 3;    // Speed control (PWM)
const int CURRENT_SENSOR_PIN = A0;  // Current sensor
const unsigned long WATCHDOG_TIMEOUT = 1500; // ms
unsigned long lastCommandTime = 0;
bool motorStopped = true;

void setup() {
  analogWrite(AN2, 0);
  pinMode(IN2, OUTPUT);
  pinMode(AN2, OUTPUT);
  pinMode(CURRENT_SENSOR_PIN, INPUT);
  Serial.begin(115200);
  stopMotor();
  lastCommandTime = millis();
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "EXTEND") {
      extend();
      Serial.println("DONE");
      lastCommandTime = millis();
      motorStopped = false;
    } else if (cmd == "RETRACT") {
      retract();
      Serial.println("DONE");
      lastCommandTime = millis();
      motorStopped = false;
    } else if (cmd == "STOP") {
      stopMotor();
      Serial.println("DONE");
      lastCommandTime = millis();
      motorStopped = true;
    } else if (cmd == "READ") {
      int current = analogRead(CURRENT_SENSOR_PIN);
      Serial.print("CURRENT:");
      Serial.println(current);
      lastCommandTime = millis();
    } else if (cmd == "PING") {
      Serial.println("PONG");
      lastCommandTime = millis();
    }
  }
  // Watchdog: stop if no command for timeout
  if (!motorStopped && (millis() - lastCommandTime > WATCHDOG_TIMEOUT)) {
    stopMotor();
    motorStopped = true;
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
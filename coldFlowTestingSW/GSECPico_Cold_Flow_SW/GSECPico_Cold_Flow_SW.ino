#include <Servo.h>
Servo fuelServo; //Initialize fuel servo object
Servo oxServo; //Initialize ox servo object

const int FUEL_PWM_PIN = 7; //Attach fuel servo to GPIO 7 (pin 10)
const int FUEL_CMD_PIN = 2; //Specify the fuel servo logic command pin as GPIO 2 (pin 4)
const int OX_PWM_PIN = 10; //Attach ox servo to GPIO 10 (pin 14)
const int OX_CMD_PIN = 5; //Specify the ox servo logic command pin as GPIO 5 (pin 7)

const int OX_OPEN_ANGLE = 715; //Define the pulse width that means "open"
const int OX_CLOSE_ANGLE = 1700; //Define the pulse width that means "close"
const int FUEL_OPEN_ANGLE = 550;
const int FUEL_CLOSE_ANGLE = 1500;

void setup() {
  pinMode(FUEL_CMD_PIN, INPUT);
  pinMode(OX_CMD_PIN, INPUT);
  fuelServo.attach(FUEL_PWM_PIN, 500, 2500);
  oxServo.attach(OX_PWM_PIN, 500, 2500);
}

//Detect if the logic control data pin's state, and adjust the position of the servo accordingly
void loop() {
  if (digitalRead(FUEL_CMD_PIN) == LOW) { //Logic "flipped" due to GSEC's (a Raspberry Pi 5) GPIO being set to high upon bootup on output pin. Adjust accordingly, if different GSEC GPIO used
    fuelServo.writeMicroseconds(FUEL_CLOSE_ANGLE);
  }
  if (digitalRead(FUEL_CMD_PIN) == HIGH) {
    fuelServo.writeMicroseconds(FUEL_OPEN_ANGLE);
  }
  if (digitalRead(OX_CMD_PIN) == LOW) {
    oxServo.writeMicroseconds(OX_CLOSE_ANGLE);
  }
  if (digitalRead(OX_CMD_PIN) == HIGH) {
    oxServo.writeMicroseconds(OX_OPEN_ANGLE);
  }
  
}
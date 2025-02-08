#include <Servo.h>
Servo N2OFillServo; //Initialize servo object

const int MAIN_PWM_PIN = 7; //Attach servo to GPIO 7 (pin 10)
const int MAIN_CMD_PIN = 2; //Specify the servo logic command pin as GPIO 2 (pin 4)
const int OPEN_ANGLE = 15; //Define the angle that means "open"
const int CLOSE_ANGLE = 165; //Define the angle that means "close"

void setup() {
  Serial.begin(115200); // Initialize serial communication
  randomSeed(analogRead(0));
  N2OFillServo.attach(MAIN_PWM_PIN);
  pinMode(MAIN_CMD_PIN, INPUT);
}

void loop() {
  int randomNumbers[7]; 
  // Generate 7 random integers and store them in an array
  for (int i = 0; i < 7; i++) {
    randomNumbers[i] = random(0, 100); // Random integer between 0 and 99
  }
  
  //Send the random integers to the GSEC
  for (int i = 0; i < 7; i++) {
    Serial.print(randomNumbers[i]);
    Serial.print(" ");  //Space-separated values
  }
  Serial.println();  //Newline to indicate end of data

  //Detect if the logic control data pin's state, and adjust the position of the servo accordingly
  if (digitalRead(MAIN_CMD_PIN) == HIGH) {
    N2OFillServo.write(OPEN_ANGLE);
  }
  if (digitalRead(MAIN_CMD_PIN) == LOW) {
    N2OFillServo.write(CLOSE_ANGLE);
  }
}


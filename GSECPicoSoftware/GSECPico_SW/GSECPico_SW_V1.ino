#include <Servo.h>
Servo N2OServo; //Initialize servo object
const int N2O_FILL_PWM_PIN = 6; //Attach servo to GPIO 6 (pin 9)
const int N2O_FILL_CMD_PIN = 2; //Specify the servo logic command pin as GPIO 2 (pin 4)
const int RANDOM_SEED_PIN = 28; //Setup pin (GPIO28/pin34) for random seed acquisition via analogRead
const int CTRL_ANGLE = 90; //Define the angle that means "open"

void setup() {
  Serial.begin(115200); // Initialize serial communication
  randomSeed(analogRead(RANDOM_SEED_PIN));
  N2OServo.attach(N2O_FILL_PWM_PIN);
  pinMode(N2O_FILL_CMD_PIN, INPUT); 
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
  if (digitalRead(N2O_FILL_CMD_PIN) == LOW) { //Logic "flipped" due to GSEC's (a Raspberry Pi 5) GPIO being set to high upon bootup on output pin. Adjust accordingly, if different GSEC GPIO used
    N2OServo.write(CTRL_ANGLE);
  }
  if (digitalRead(N2O_FILL_CMD_PIN) == HIGH) {
    N2OServo.write(0);
  }
}
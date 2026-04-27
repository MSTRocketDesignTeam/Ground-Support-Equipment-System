#include <Arduino.h>
#include <Servo.h>

int GSECUServoPwrSwitchPin = 28;
int fuelValvePWMPin        = 26;
int oxValvePWMPin          = 27;

Servo fuelValve;
Servo oxValve;

const int SERVO_OPEN_ANGLE_US = 1140;
const int SERVO_CLOSE_ANGLE_US = 2500;

const byte NUM_CHARS = 4;
char receivedChars[NUM_CHARS];
bool newData = false;

void recv_with_start_end_markers();

void setup() {
  Serial.begin(115200);
  pinMode(GSECUServoPwrSwitchPin, OUTPUT);
  digitalWrite(GSECUServoPwrSwitchPin, HIGH);
  fuelValve.attach(fuelValvePWMPin, 500, 2500);
  oxValve.attach(oxValvePWMPin, 500, 2500);
}

void loop() {
  recv_with_start_end_markers();

  if (newData == true) {
    if (receivedChars[0] == 'C') {
      fuelValve.writeMicroseconds(SERVO_CLOSE_ANGLE_US);
    } else if (receivedChars[0] == 'O') {
      fuelValve.writeMicroseconds(SERVO_OPEN_ANGLE_US);
    }

    if (receivedChars[1] == 'C') {
      oxValve.writeMicroseconds(SERVO_CLOSE_ANGLE_US);
    } else if (receivedChars[1] == 'O') {
      oxValve.writeMicroseconds(SERVO_OPEN_ANGLE_US);
    }

    newData = false; 
  }
}

void recv_with_start_end_markers() {
  static boolean recvInProgress = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char rc;

  while (Serial.available() > 0 && newData == false) {
    rc = Serial.read();

    if (recvInProgress == true) {
      if (rc != endMarker) {
        receivedChars[ndx] = rc;
        ndx++;
        if (ndx >= NUM_CHARS) {
          ndx = NUM_CHARS - 1;
        }
      } else {
        receivedChars[ndx] = '\0';
        recvInProgress = false;
        ndx = 0;
        newData = true;
      }
    } else if (rc == startMarker) {
      recvInProgress = true;
    }
  }
}
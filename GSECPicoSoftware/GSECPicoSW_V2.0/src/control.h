#ifndef CONTROL_
#define CONTROL_

#include <Arduino.h>
#include <Servo.h>

//Defining control angles of the servos
const int SERVO_OPEN_ANGLE_US = 1140;
const int SERVO_CLOSE_ANGLE_US = 2500;
const int SERVO_PARTIAL_ANGLE_US = 2100;

void update_GSE_states(char GSECUServoPwrSwitchState, char GN2FillValveState, char N2OFillValveState, char QDRelayState, char ignitionRelayState,
                        int GSECUServoPwrSwitchPin, Servo &GN2FillValve, Servo &N2OFillValve, int QDRelayPin, int ignitionRelayPin);

#endif

#include <Arduino.h>
#include <Servo.h>
#include <control.h>

// Purpose: update GSE control hardware states (valve positions, igniter states, etc.) based on ctrlString index values. 
// Pre: 
// Post: 
void update_GSE_states(char GSECUServoPwrSwitchState, char GN2FillValveState, char N2OFillValveState, char QDRelayState, char ignitionRelayState,
                        int GSECUServoPwrSwitchPin, Servo &GN2FillValve, Servo &N2OFillValve, int QDRelayPin, int ignitionRelayPin) {
    if (GSECUServoPwrSwitchState == 'L') {
        digitalWrite(GSECUServoPwrSwitchPin, LOW);
    } else if (GSECUServoPwrSwitchState == 'H') {
        digitalWrite(GSECUServoPwrSwitchPin, HIGH);
    }

    if (GN2FillValveState == 'C') {
        GN2FillValve.writeMicroseconds(SERVO_CLOSE_ANGLE_US);
    } else if (GN2FillValveState == 'O') {
        GN2FillValve.writeMicroseconds(SERVO_OPEN_ANGLE_US);
    }

    if (N2OFillValveState == 'C') {
        N2OFillValve.writeMicroseconds(SERVO_CLOSE_ANGLE_US);
    } else if (N2OFillValveState == 'O') {
        N2OFillValve.writeMicroseconds(SERVO_OPEN_ANGLE_US);
    } else if (N2OFillValveState == 'P') {
        N2OFillValve.writeMicroseconds(SERVO_PARTIAL_ANGLE_US);
    }

    if (QDRelayState == 'L') {
        digitalWrite(QDRelayPin, LOW);
    } else if (QDRelayState == 'H') {
        digitalWrite(QDRelayPin, HIGH);
    }

    if (ignitionRelayState == 'L') {
        digitalWrite(ignitionRelayPin, LOW);
    } else if (ignitionRelayState == 'H') {
        digitalWrite(ignitionRelayPin, HIGH);
    }
}
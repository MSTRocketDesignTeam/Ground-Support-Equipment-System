#include <Arduino.h>
#include <Servo.h>
#include <control.h>
#include <RPi_Pico_TimerInterrupt.h>
#include <DAQ.h>


// -------------------- Pin Setup --------------------
int GSECUServoPwrSwitchPin = 28;
int GN2FillValvePWMPin     = 26;
int N2OFillValvePWMPin     = 27;
int QDRelayPin             = 20;
int ignitionRelayPin       = 22;

Servo GN2FillValve;
Servo N2OFillValve;

// -------------------- Control States --------------------
// Loop-owned states
char GSECUServoPwrSwitchState;
char GN2FillValveState;
char N2OFillValveState;
char LECUServoPwrSwitchState;
char N2OMainValvePurgeState;
char mainValvesState;
char QDRelayState;
char ignitionRelayState;
char throttlingAlgorithmState;

// Snapshot for ISR-safe transmission
volatile char ctrlSnapshot[4];  
// [0]=LECU Servo Pwr, [1]=Purge, [2]=Main Valves, [3]=Throttle Algo

// -------------------- Serial RX --------------------
const byte NUM_CHARS = 10;
char receivedChars[NUM_CHARS];
bool newData = false;

// -------------------- Timer --------------------
RPI_PICO_Timer ITimer0(0);
const int LECU_CTRLSTRING_TX_INTERVAL = 10;   // in ms
volatile bool sendCtrlFlag = false;

// -------------------- Function Declarations --------------------
void recv_with_start_end_markers();
void process_ctrl_packet();
void update_ctrl_snapshot();
void send_ctrl_string();
bool send_LECU_ctrlString_ISR(struct repeating_timer *t);



void setup() {
  Serial.begin(115200);
  Serial1.begin(115200);
  pinMode(GSECUServoPwrSwitchPin, OUTPUT);
  pinMode(QDRelayPin, OUTPUT);
  pinMode(ignitionRelayPin, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);

  GN2FillValve.attach(GN2FillValvePWMPin, 500, 2500);
  N2OFillValve.attach(N2OFillValvePWMPin, 500, 2500);

  // Timer ISR every 100 ms
  ITimer0.attachInterruptInterval(LECU_CTRLSTRING_TX_INTERVAL*1000, send_LECU_ctrlString_ISR);
}


void loop() {
  


  // 1. Receive incoming serial data
  recv_with_start_end_markers();

  // 2. Process new packet
  if (newData) {
    process_ctrl_packet();
    newData = false;
  }

  // 3. Handle periodic transmission (triggered by ISR)
  if (sendCtrlFlag) {
    sendCtrlFlag = false;
    send_ctrl_string();
  }

  // Optional: DAQ reading (keep outside ISR)
  // read_DAQ_module(...);
  
}

void process_ctrl_packet() {

  // ---- Critical section: copy shared RX buffer ----
  noInterrupts();
  GSECUServoPwrSwitchState = receivedChars[0];
  GN2FillValveState        = receivedChars[1];
  N2OFillValveState        = receivedChars[2];
  LECUServoPwrSwitchState  = receivedChars[3];
  N2OMainValvePurgeState   = receivedChars[4];
  mainValvesState          = receivedChars[5];
  QDRelayState             = receivedChars[6];
  ignitionRelayState       = receivedChars[7];
  throttlingAlgorithmState = receivedChars[8];
  interrupts();

  // ---- Update hardware (interrupts ENABLED) ----
  update_GSE_states(
    GSECUServoPwrSwitchState,
    GN2FillValveState,
    N2OFillValveState,
    QDRelayState,
    ignitionRelayState,
    GSECUServoPwrSwitchPin,
    GN2FillValve,
    N2OFillValve,
    QDRelayPin,
    ignitionRelayPin
  );

  // ---- Update snapshot for transmission ----
  update_ctrl_snapshot();
}


void update_ctrl_snapshot() {
  noInterrupts();
  ctrlSnapshot[0] = LECUServoPwrSwitchState;
  ctrlSnapshot[1] = N2OMainValvePurgeState;
  ctrlSnapshot[2] = mainValvesState;
  ctrlSnapshot[3] = throttlingAlgorithmState;
  interrupts();
}


bool send_LECU_ctrlString_ISR(struct repeating_timer *t) {
  sendCtrlFlag = true;  // Set flag only
  return true;
}



void send_ctrl_string() {

  // Local copy prevents mid-print corruption
  char localCopy[4];

  noInterrupts();
  for (int i = 0; i < 4; i++) {
    localCopy[i] = ctrlSnapshot[i];
  }
  interrupts();

  Serial1.print('<');
  Serial1.print(localCopy[0]);
  Serial1.print(localCopy[1]);
  if (localCopy[1] == 'O') {
    digitalWrite(LED_BUILTIN, HIGH);
  } else if (localCopy[1] == 'C') {
    digitalWrite(LED_BUILTIN, LOW);
  }
  Serial1.print(localCopy[2]);
  Serial1.print(localCopy[3]);
  Serial1.print('>');
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
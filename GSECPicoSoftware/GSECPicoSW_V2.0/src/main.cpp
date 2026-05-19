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
char prevLECUServoPwrSwitchState;
char prevN2OMainValvePurgeState;
char prevmainValvesState;
char prevthrottlingAlgorithmState;

// ------------------- Sensor Data -----------------------
volatile uint32_t AI0Reading;
volatile uint32_t AI1Reading;
volatile uint32_t AI2Reading;
volatile uint32_t AI3Reading;
volatile uint32_t TC1Reading;
volatile uint32_t TC2Reading;
volatile uint32_t TC3Reading;

volatile uint32_t LECUAI0Reading;
volatile uint32_t LECUAI1Reading;
volatile uint32_t LECUAI2Reading;
volatile uint32_t LECUAI3Reading;
volatile uint32_t LECUAI4Reading;
volatile uint32_t LECUAI5Reading;
volatile uint32_t LECUAI6Reading;
volatile uint32_t LECUTC1Reading;
volatile uint32_t LECUTC2Reading;
volatile uint32_t LECUTC3Reading;

volatile uint32_t *sensorReadingArr[] = {&LECUAI0Reading, &LECUAI1Reading, &LECUAI2Reading, &LECUAI3Reading, &LECUAI4Reading, &LECUAI5Reading, &LECUAI6Reading, &LECUTC1Reading, &LECUTC2Reading, &LECUTC3Reading};

// Snapshot for ISR-safe transmission
volatile char ctrlSnapshot[4];  
// [0]=LECU Servo Pwr, [1]=Purge, [2]=Main Valves, [3]=Throttle Algo

// -------------------- Serial RX --------------------
const byte NUM_CHARS = 10;
char receivedChars[NUM_CHARS];
bool newData = false;

const byte NUM_BYTES = 64;
char receivedBytes[NUM_BYTES];
bool LECUnewData = false;

// -------------------- Timer --------------------
RPI_PICO_Timer ITimer0(0);
const int ISR_INTERVAL = 10;   // in ms
volatile bool sendCtrlFlag = false;
volatile bool DAQFlag = false;
volatile uint32_t tick = 0;


// -------------------- Function Declarations --------------------
void recv_with_start_end_markers();
void recv_sensor_data();
void process_sensor_data();
void process_ctrl_packet();
void update_ctrl_snapshot();
void send_ctrl_string();
void send_sensor_data();
bool Timer_ISR(struct repeating_timer *t);



void setup() {
  
  pinMode(GSECUServoPwrSwitchPin, OUTPUT);
  pinMode(QDRelayPin, OUTPUT);
  pinMode(ignitionRelayPin, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);

  GN2FillValve.attach(GN2FillValvePWMPin, 500, 2500);
  N2OFillValve.attach(N2OFillValvePWMPin, 500, 2500);

  init_DAQ();
  Serial.begin(115200);
  Serial1.begin(115200);

  delay(1500);

  // Timer ISR every 10 ms
  ITimer0.attachInterruptInterval(ISR_INTERVAL*1000, Timer_ISR);
}



void loop() {
  // Receive incoming serial data
  recv_with_start_end_markers();
  recv_sensor_data();

  // Process new packet
  if (newData) {
    process_ctrl_packet();
    newData = false;
  }
  
  if (LECUnewData) {
    process_sensor_data();
    LECUnewData = false;
  }

  if (sendCtrlFlag) {
    sendCtrlFlag = false;
    if (((prevLECUServoPwrSwitchState != LECUServoPwrSwitchState) || (prevN2OMainValvePurgeState != N2OMainValvePurgeState) || (prevmainValvesState != mainValvesState) || (prevthrottlingAlgorithmState != throttlingAlgorithmState))) {
      send_ctrl_string();
    }
  }

  if (DAQFlag) {
    DAQFlag = false;
    read_DAQ_module(AI0Reading, AI1Reading, AI2Reading, AI3Reading, TC1Reading, TC2Reading, TC3Reading);
    send_sensor_data();
  }
  
  prevLECUServoPwrSwitchState = LECUServoPwrSwitchState;
  prevN2OMainValvePurgeState = N2OMainValvePurgeState;
  prevmainValvesState = mainValvesState;
  prevthrottlingAlgorithmState = throttlingAlgorithmState;
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


void recv_sensor_data() {
  static bool receiving = false;
  static uint8_t idx = 0;

  while (Serial1.available() > 0) {

    uint8_t b = Serial1.read();
    digitalWrite(LED_BUILTIN, HIGH);

    if (!receiving) {

      if (b == '<') {
        receiving = true;
        idx = 0;
      }

    } else {

      receivedBytes[idx++] = b;

      if (idx >= 40) {
        LECUnewData = true;
        receiving = false;
        idx = 0;
      }
    }
  }
}


void process_sensor_data() {
  noInterrupts();
  for (int i = 0; i < 10; i++) {

    uint32_t val;

    memcpy(&val, &receivedBytes[i * 4], 4);

    *sensorReadingArr[i] = val;
  }
  interrupts();
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


void send_ctrl_string() {

  char localCopy[4];
  
  noInterrupts();
  for (int i = 0; i < 4; i++) {
    localCopy[i] = ctrlSnapshot[i];
  }
  interrupts();

  Serial1.print('<');
  Serial1.print(localCopy[0]);
  Serial1.print(localCopy[1]);
  Serial1.print(localCopy[2]);
  Serial1.print(localCopy[3]);
  Serial1.print('>');
}

void send_sensor_data() {
  if ((Serial.availableForWrite() < 64)) {
    return;
  }

  Serial.print(AI0Reading);
  Serial.print(',');
  Serial.print(AI1Reading);
  Serial.print(',');
  Serial.print(AI2Reading);
  Serial.print(',');
  Serial.print(AI3Reading);
  Serial.print(',');
  Serial.print(TC1Reading);
  Serial.print(',');
  Serial.print(TC2Reading);
  Serial.print(',');
  Serial.print(TC3Reading);
  Serial.print(',');
  Serial.print(LECUAI0Reading);
  Serial.print(',');
  Serial.print(LECUAI1Reading);
  Serial.print(',');
  Serial.print(LECUAI2Reading);
  Serial.print(',');
  Serial.print(LECUAI3Reading);
  Serial.print(',');
  Serial.print(LECUAI4Reading);
  Serial.print(',');
  Serial.print(LECUAI5Reading);
  Serial.print(',');
  Serial.print(LECUAI6Reading);
  Serial.print(',');
  Serial.print(LECUTC1Reading);
  Serial.print(',');
  Serial.print(LECUTC2Reading);
  Serial.print(',');
  Serial.println(LECUTC3Reading);
}

bool Timer_ISR(struct repeating_timer *t) {
  tick++;
  if (tick % 5 == 0) {      // every 5 ticks aka 50 ms
    sendCtrlFlag = true;
  }
  if (tick % 10 == 0) {     // every 10 ticks aka 100 ms
    DAQFlag = true;
  }
  
  return true;
}


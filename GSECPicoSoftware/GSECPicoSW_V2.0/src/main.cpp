#include <Arduino.h>
#include <Servo.h>
#include <control.h>
#include <RPi_Pico_TimerInterrupt.h>
#include <DAQ.h>


// Initializing pin mapping for the GSECPM
int GSECUServoPwrSwitchPin = 28;
int GN2FillValvePWMPin = 26;
Servo GN2FillValve;
int N2OFillValvePWMPin = 27;
Servo N2OFillValve;
int QDRelayPin = 20;
int ignitionRelayPin = 22;

// Initalizing the state variables (ignores start and end markers, as they are discarded by the recv function)
char GSECUServoPwrSwitchState;
char GN2FillValveState;
char N2OFillValveState;
char LECUServoPwrSwitchState;
char N2OMainValvePurgeState;
char mainValvesState;
char QDRelayState;
char ignitionRelayState;
char throttlingAlgorithmState;

// Initializing timer objects and parameters
unsigned long DAQ_READ_INTERVAL_MS = 1500;
RPI_PICO_Timer ITimer0(0);
unsigned long SENSOR_DATA_TX_INTERVAL_MS = 400;  // Interval in milliseconds
RPI_PICO_Timer ITimer1(1);

// Initializing the sensor readings as volatiles because they might work better when modified inside an ISR?
volatile uint32_t AI0, AI1, AI2, AI3;
volatile uint32_t TC1, TC2, TC3;

// Defining the packet structure (ignores start and end markers, as they are discarded by the recv function)
const byte NUM_CHARS = 10;
//char receivedChars[NUM_CHARS] = {GSECUServoPwrSwitchState, GN2FillValveState, N2OFillValveState, LECUServoPwrSwitchState, N2OMainValvePurgeState, mainValvesState, QDRelayState, ignitionRelayState, throttlingAlgorithmState};
char receivedChars[NUM_CHARS];
boolean newData = false;

// Miscellaneous com functions
void recvWithStartEndMarkers();


// ISR functions (not all are used)
bool sendSensorDataMsg(struct repeating_timer *t); 
bool sendLECUCtrlString(struct repeating_timer *t);
bool readDAQ(struct repeating_timer *t);


void setup() {
  Serial.begin(115200);
  pinMode(GSECUServoPwrSwitchPin, OUTPUT);
  pinMode(QDRelayPin, OUTPUT);
  pinMode(ignitionRelayPin, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  GN2FillValve.attach(GN2FillValvePWMPin, 500, 2500);
  N2OFillValve.attach(N2OFillValvePWMPin, 500, 2500);
  init_DAQ();
  //ITimer1.attachInterruptInterval(SENSOR_DATA_TX_INTERVAL_MS * 1000, sendSensorDataMsg);
  //ITimer0.attachInterruptInterval(DAQ_READ_INTERVAL_MS * 1000, readDAQ);
}




void loop() {
  /*
  recvWithStartEndMarkers();
  if (newData) {
    GSECUServoPwrSwitchState = receivedChars[0];
    GN2FillValveState        = receivedChars[1];
    N2OFillValveState        = receivedChars[2];
    LECUServoPwrSwitchState  = receivedChars[3];
    N2OMainValvePurgeState   = receivedChars[4];
    mainValvesState          = receivedChars[5];
    QDRelayState             = receivedChars[6];
    ignitionRelayState       = receivedChars[7];
    throttlingAlgorithmState = receivedChars[8];
    update_GSE_states(GSECUServoPwrSwitchState, GN2FillValveState, N2OFillValveState, QDRelayState, ignitionRelayState,
                    GSECUServoPwrSwitchPin, GN2FillValve, N2OFillValve, QDRelayPin, ignitionRelayPin);
    newData = false;
  }
  //read_DAQ_module(AI0, AI1, AI2, AI3, TC1, TC2, TC3);
  */
  read_DAQ_module(AI0, AI1, AI2, AI3, TC1, TC2, TC3);
  Serial.print(AI0);
  Serial.print(' ');
  Serial.print(AI1);
  Serial.print(' ');
  Serial.print(AI2);
  Serial.print(' ');
  Serial.print(AI3);
  Serial.print(' ');
  Serial.print(TC1);
  Serial.print(' ');
  Serial.print(TC2);
  Serial.print(' ');
  Serial.print(TC3);
  Serial.println();
  /*
  _u32data_t CONV_DATA; 
  CONV_DATA.DWORD = 0x00000000;

  _u32data_t TEMP_SNSR_DATA;
  TEMP_SNSR_DATA.DWORD = 0x00000000;

  _u16data_t ADC_CRC;
  ADC_CRC.WORD = 0x0000;

  uint64_t CALC_CRC = 0x000000000000;

  if (Serial) 
  {            
    delay(1500);                                                                // Delay for 1.5s.
    if(CONV_START(MUX_VINP_CH0 | MUX_VINN_AGND) == 0x13)                         // Convert CH0(+) and AGND(-) channel (singlez) and check Data-Ready(DR) Bit of STATUS Byte.               
    {  
      CONV_DATA.DWORD = SPI_RD(_ADCDATA_, ADC_CRC, CALC_CRC);                 // Read Signal Conversion data.     
      Serial.print((CONV_DATA.DWORD & 0x00FFFFFF), DEC);
      Serial.println();
    }
    else                                                                        // No new Data-Ready? 
    {
      Serial.print(" Invalid Measurement!!! Displaying previous data. ");     // Print " Invalid Measurement!!! Displaying previous data. ".                                                          
      Serial.println();
    }     
  }
  */
}



void recvWithStartEndMarkers() {
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
        receivedChars[ndx] = '\0'; // terminate the string
        recvInProgress = false;
        ndx = 0;
        newData = true;
      }
    } else if (rc == startMarker) {
      recvInProgress = true;
    }
  }
}




bool sendSensorDataMsg(struct repeating_timer *t) {
  Serial.print(AI0);
  Serial.print(' ');
  Serial.print(AI1);
  Serial.print(' ');
  Serial.print(AI2);
  Serial.print(' ');
  Serial.print(AI3);
  Serial.print(' ');
  Serial.print(TC1);
  Serial.print(' ');
  Serial.print(TC2);
  Serial.print(' ');
  Serial.print(TC3);
  Serial.println();
  return true;
}

bool sendLECUCtrlString(struct repeating_timer *t) {
  Serial2.print('<');
  Serial2.print(LECUServoPwrSwitchState);
  Serial2.print(N2OMainValvePurgeState);
  Serial2.print(mainValvesState);
  Serial2.print(throttlingAlgorithmState);
  Serial2.print('>');
  return true;
}

bool readDAQ(struct repeating_timer *t) {
  read_DAQ_module(AI0, AI1, AI2, AI3, TC1, TC2, TC3);
  return true;
}
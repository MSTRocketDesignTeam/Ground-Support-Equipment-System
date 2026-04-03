#include "DAQ.h"

// Pin Assignments
int MCP3564_MISO_PIN = 4;   
int MCP3564_MOSI_PIN = 7;
int MCP3564_SCK_PIN = 6;
int MCP3564_CS_PIN = 5;

int TCIC_MISO_PIN  = 8;
int TCIC_SCK_PIN   = 10;
int TC1_CS_PIN     = 9;   // GN2 TC
int TC2_CS_PIN     = 13;   // Internal TC
int TC3_CS_PIN     = 12;   // N2O TC

// MAX31855 TCIC SPI Settings
SPISettings tcSPISettings(4000000, MSBFIRST, SPI_MODE0);

// MCP3564 ADC Settings
SPISettings adcSPISettings(12000000, MSBFIRST, SPI_MODE0);         // SPI Bus is 4MHz, MSb-First, Mode 0,0.  


// -------------------------
// MAX31855 read (SPI1)
// -------------------------
uint32_t read_MAX31855(int csPin) {
    SPI1.beginTransaction(tcSPISettings);
    digitalWrite(csPin, LOW);

    uint32_t raw = 0;
    raw |= ((uint32_t)SPI1.transfer(0x00) << 24);
    raw |= ((uint32_t)SPI1.transfer(0x00) << 16);
    raw |= ((uint32_t)SPI1.transfer(0x00) << 8);
    raw |= ((uint32_t)SPI1.transfer(0x00));

    digitalWrite(csPin, HIGH);
    SPI1.endTransaction();

    return raw;
}

// -------------------------
// MCP3564 read (SPI0)
// -------------------------
uint32_t analog_read_MCP3564_mux_chan(int csPin, int posMuxChanByte, int negMuxChanByte) {
    

    SPI.beginTransaction(adcSPISettings);
    _u32data_t CONV_DATA; 
    CONV_DATA.DWORD = 0x00000000;
    _u16data_t ADC_CRC;
    ADC_CRC.WORD = 0x0000;
    uint64_t CALC_CRC = 0x000000000000;

    delay(1400);   // Delay for 1.4s. It appears that the lower limit for this is between 1300 and 1400ms

    if(CONV_START(posMuxChanByte | negMuxChanByte) == 0x13) {     // Convert posMuxChanByte(+) and negMuxChanByte(-) channel ("single ended" reading) and check Data-Ready(DR) Bit of STATUS Byte.               
        CONV_DATA.DWORD = SPI_RD(_ADCDATA_, ADC_CRC, CALC_CRC);      // Read Signal Conversion data.
    }  // ADC Readings will be uncharacteristically perfectly stable at zero if there is no valid reading of the analog channel

    SPI.endTransaction();

    // Masking the "insignificant" status bits and padding, and returning only the lowest 24 bits (the actual ADC conversion reading)
    return (CONV_DATA.DWORD & 0x00FFFFFF);   // Returns in uint_32_t format, but directly in byte form
}

// -------------------------
// Initialization
// -------------------------
void init_DAQ() {
    // Chip Select Pins
    pinMode(MCP3564_CS_PIN, OUTPUT);
    pinMode(TC1_CS_PIN, OUTPUT);
    pinMode(TC2_CS_PIN, OUTPUT);
    pinMode(TC3_CS_PIN, OUTPUT);

    digitalWrite(MCP3564_CS_PIN, HIGH);
    digitalWrite(TC1_CS_PIN, HIGH);
    digitalWrite(TC2_CS_PIN, HIGH);
    digitalWrite(TC3_CS_PIN, HIGH);

    // SPI0 → MCP3564
    SPI.setRX(MCP3564_MISO_PIN);   // MISO
    SPI.setTX(MCP3564_MOSI_PIN);   // MOSI
    SPI.setSCK(MCP3564_SCK_PIN);   // SCK
    SPI.setCS(MCP3564_CS_PIN);     // CS 
    SPI.begin();
    SPI.beginTransaction(adcSPISettings);
    // Configure ADC
    MCP3x6x_CONFIG();    // MCP3564 Register Configuration.
    SPI.endTransaction();
    delay(10);         // Theoretical min is 256 AMCK cycles (256us if SCK is at 1 MHz??) (see T_ADC_SETUP in datasheet for MCP3564)

    // SPI1 → MAX31855
    SPI1.setRX(TCIC_MISO_PIN);     // MISO
    SPI1.setSCK(TCIC_SCK_PIN);     // SCK
    SPI1.begin();    
}

// -------------------------
// High‑level DAQ read function (pass by reference parameters so that they can be modified)
// -------------------------
void read_DAQ_module(
    volatile uint32_t &AI0Reading,
    volatile uint32_t &AI1Reading,
    volatile uint32_t &AI2Reading,
    volatile uint32_t &AI3Reading,
    volatile uint32_t &TC1Reading,
    volatile uint32_t &TC2Reading,
    volatile uint32_t &TC3Reading
) {
    // Read ADC channels
    AI0Reading = analog_read_MCP3564_mux_chan(MCP3564_CS_PIN, MUX_VINP_CH0, MUX_VINN_AGND);
    AI1Reading = analog_read_MCP3564_mux_chan(MCP3564_CS_PIN, MUX_VINP_CH1, MUX_VINN_AGND);
    AI2Reading = analog_read_MCP3564_mux_chan(MCP3564_CS_PIN, MUX_VINP_CH2, MUX_VINN_AGND);
    AI3Reading = analog_read_MCP3564_mux_chan(MCP3564_CS_PIN, MUX_VINP_CH3, MUX_VINN_AGND);
    
    // Read thermocouples
    TC1Reading = read_MAX31855(TC1_CS_PIN);
    TC2Reading = read_MAX31855(TC2_CS_PIN);
    TC3Reading = read_MAX31855(TC3_CS_PIN);
}

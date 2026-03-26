#include <SPI.h>
#include "MCP3x6x_Type_Definitions.h"


#define ENABLE_SPI_CRC                                  // Enable Communication-CRC.
//#define DISABLE_SPI_CRC                                 // Disable Communication-CRC.

//#define ENABLE_ADCCONV_FASTCMD                          // Enable ADC Conversion Fast-CMD.
#define DISABLE_ADCCONV_FASTCMD                         // Disable ADC Conversion Fast-CMD.


const uint8_t PIN_SPI_nCS = 5;                        // Arduino Zero Pin D10 is MCP3564 nCS. //Pi Pico (GP5) -> Arduino 5?
 
const uint8_t _WRT_CTRL_ = 0b01000010;                // MCP3564(R) Write-CMD Command-Byte.
const uint8_t _RD_CTRL_ = 0b01000001;                 // MCP3564(R) Read-CMD Command-Byte.

const uint8_t _DONT_CARE0_ = 0b01000000;              // Don't-Care Fast-CMD.
const uint8_t _DONT_CARE1_ = 0b01000100;              // Don't-Care Fast-CMD.
const uint8_t _DONT_CARE2_ = 0b01001000;              // Don't-Care Fast-CMD.
const uint8_t _DONT_CARE3_ = 0b01001100;              // Don't-Care Fast-CMD.
const uint8_t _DONT_CARE4_ = 0b01010000;              // Don't-Care Fast-CMD.
const uint8_t _DONT_CARE5_ = 0b01010100;              // Don't-Care Fast-CMD.
const uint8_t _DONT_CARE6_ = 0b01011000;              // Don't-Care Fast-CMD.
const uint8_t _DONT_CARE7_ = 0b01011100;              // Don't-Care Fast-CMD.
const uint8_t _DONT_CARE8_ = 0b01100000;              // Don't-Care Fast-CMD.
const uint8_t _DONT_CARE9_ = 0b01100100;              // Don't-Care Fast-CMD.
const uint8_t _ADC_CONV_STRST_ = 0b01101000;          // ADC Conversion-Start/Restart Fast-CMD (Overwrites ADC_MODE[1:0] = 0b11).
const uint8_t _ADC_STBY_MODE_ = 0b01101100;           // ADC Standby Mode Fast-CMD (Overwrites ADC_MODE[1:0] = 0b10).
const uint8_t _ADC_SHTDN_MODE_ = 0b01110000;          // ADC Shutdown Mode Fast-CMD (Overwrites ADC_MODE[1:0] = 0b00).
const uint8_t _DEV_FSHTDN_MODE_ = 0b01110100;         // Device Full-Shutdown Mode Fast-CMD (Overwrites CONFIG0[7:0] = 0x00).
const uint8_t _DEV_FRESET_ = 0b01111000;              // Device Full-Reset Fast-CMD (Overwrites entire register map to default settings).
const uint8_t _RTRV_STATUS_ = 0b01111100;             // Don't-Care Fast-CMD to retrieve STATUS Byte.


void SPI_WRT(uint8_t, uint32_t);                      // SPI Write-CMD Function Prototype.

uint32_t SPI_RD(uint8_t, _u16data_t&, uint64_t&);     // SPI Read-CMD Function Prototype.

uint8_t CONV_START(uint8_t);                          // ADC Conversion-Start Prototype.

uint8_t RETRIEVE_STATUS(void);                        // ADC STATUS Byte Retrieval Function Prototype.

void SPI_FASTCMD(uint8_t);                            // SPI Fast-CMD Function Prototype.

uint64_t SPI_COMMCRC(_u64data_t);                     // SPI Communication-CRC Function Prototype.


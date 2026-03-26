#include <Arduino.h>
#include "MCP3x6x_Type_Definitions.h"                                   // Variable definitions header-file.
#include "MCP3x6x_ADC_Definitions.h"                                    // ADC definitions header-file.
#include "MCP3x6x_Peripheral_Definitions.h"                             // Peripheral definitions header-file.

float TEMP_SNSR(uint32_t TEMP_SNSR_OUTPUT)
{
    float TEMP_DEG_C;                                                                             // Temperature Sensor calculated floating-point value in °C.

    TEMP_DEG_C = (((float)(0x00FFFFFF & TEMP_SNSR_OUTPUT)*((float)0.00040096)*2) - 269.13);       // See MCP3564(R) datasheet for Temp Sensor Eqn.
                                                                                                  // Temp(C) = (.00040096 x ADCDATA x VREF) - 269.13. 
    return TEMP_DEG_C;                                                                            // Return calcualted temperature in °C.                                                                                                                   
}

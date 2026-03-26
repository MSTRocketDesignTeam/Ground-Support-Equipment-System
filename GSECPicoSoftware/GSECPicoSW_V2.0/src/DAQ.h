#ifndef DAQ_H
#define DAQ_H

#include <Arduino.h>
#include <SPI.h>
#include "MCP3x6x_Type_Definitions.h"                     // Variable definitions header-file.
#include "MCP3x6x_ADC_Definitions.h"                      // ADC definitions header-file.
#include "MCP3x6x_Peripheral_Definitions.h"               // Peripheral definitions header-file.
#include "MCP3x6x_SPI_Definitions.h"                      // SPI definitions header-file.


// -------------------------
// Pin Assignments
// -------------------------
extern int MCP3564_CS_PIN;
extern int TC1_CS_PIN;
extern int TC2_CS_PIN;
extern int TC3_CS_PIN;

// -------------------------
// Initialization
// -------------------------
void init_DAQ();

// -------------------------
// High‑level DAQ read function
// -------------------------
void read_DAQ_module(
    volatile uint32_t &AI0Reading,
    volatile uint32_t &AI1Reading,
    volatile uint32_t &AI2Reading,
    volatile uint32_t &AI3Reading,
    volatile uint32_t &TC1Reading,
    volatile uint32_t &TC2Reading,
    volatile uint32_t &TC3Reading
);

#endif

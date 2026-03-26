#pragma once

#include <cstdint>

typedef unsigned long long int _uint64_t;         // 64-bit Unsigned Long Long Integer Type-Def.  

union _u16data_t                                  // 16-bit Union-Structure for Communication-CRC.
{
    struct
    {
        uint8_t LOW;                              // Low-Byte of 8-, 16- and 24-bit MCP3564 Registers.
        uint8_t HIGH;                             // High-Byte of 16- and 24-bit MCP3564 Registers.
    }BYTE;
    uint16_t WORD;                                // Communication-CRC 16-bit unsigned integer data value. 
};

union _u32data_t                                  // 32-bit Union of Structures for ADC Conversion Data.
{
    struct
    {
        uint8_t LOW;                              // Low-Byte of 8-, 16- and 24-bit MCP3564 Registers.
        uint8_t HIGH;                             // High-Byte of 16- and 24-bit MCP3564 Registers.
        uint8_t UPPER;                            // Upper-Byte of 24-bit MCP3564 Registers.
        uint8_t STATUS;                           // STATUS Byte of MCP3564.
    }BYTE;                                        // ADC Conversion Data Byte Structure.
    struct
    {
        uint16_t LOW;                             // Low-Word of 16- and 24-bit MCP3564 Registers.
        uint16_t HIGH;                            // High-Word (high-byte) of 24-bit MCP3564 Registers.
    }WORD;                                        // ADC Conversion Data Word Structure. 
    uint32_t DWORD;                               // ADC Signal Convserion 32-bit unsigned integer data value. 
    float FLTWORD;                                // Temperature Sensor 32-bit floating point data value. 
};

union _u64data_t                                  // 64-bit Union of Structures for CRC Calculation.
{
    struct
    {
        uint8_t BYTE0;                            // Byte0 of 64-bit CRC Dividend.                    
        uint8_t BYTE1;                            // Byte1 of 64-bit CRC Dividend.
        uint8_t BYTE2;                            // Byte2 of 64-bit CRC Dividend.
        uint8_t BYTE3;                            // Byte3 of 64-bit CRC Dividend.
        uint8_t BYTE4;                            // Byte4 of 64-bit CRC Dividend.
        uint8_t BYTE5;                            // Byte5 of 64-bit CRC Dividend.
        uint8_t BYTE6;                            // Byte6 of 64-bit CRC Dividend.
        uint8_t BYTE7;                            // Byte7 of 64-bit CRC Dividend.            
    }BYTE;                                        // CRC Dividend Byte Structure. 
    struct
    {
        uint16_t LOW;                             // Low-Word of 64-bit CRC Dividend.
        uint16_t HIGHL;                           // Low-Word of High-Double-Word of 64-bit CRC Dividend. 
        uint16_t HIGHH;                           // High-Word of High-Double-Word of 64-bit CRC Dividend.
        uint16_t UPPER;                           // Upper-Word of 64-bit CRC Dividend.
    }WORD;                                        // CRC Dividend Word Structure. 
    struct
    {
        uint16_t LOW;                             // Low-Word of 64-bit CRC Dividend.
        uint32_t HIGH;                            // High-Double-Word of 64-bit CRC Dividend.
        uint16_t UPPER;                           // Upper-Word of 64-bit CRC Dividend.
    }DWORD;                                       // CRC Dividend Double-Word Structure. 
    uint64_t QWORD;                               // CRC Dividend 64-bit unsigned long long integer data value.                                                                 
};


/* ADCDATA REGISTER */
const uint8_t _ADCDATA_ = 0x00;               // ADCDATA Register Address.


/* CONFIG0 REGISTER */
const uint8_t _CONFIG0_ = 0x01;               // CONFIG0 Register Address.

    // CONFIG0_67 Settings
    #define CONFIG0_67_PSHTDN 0b11000000
    //#define CONFIG0_67_PSHTDN 0b10          
    //#define CONFIG0_67_PSHTDN 0b01          
    #define CONFIG0_67_FSHTDN 0b00000000

    // CLK_SEL Settings
    #define CLK_SEL_INTOSC_CLKOUT 0b00110000
    #define CLK_SEL_INTOSC_NOCLKOUT 0b00100000
    #define CLK_SEL_EXTCLK01 0b00010000
    #define CLK_SEL_EXTCLK00 0b00000000

    // CS_SEL Settings
    #define CS_SEL_150 0b00001100
    #define CS_SEL_37 0b00001000
    #define CS_SEL_09 0b00000100
    #define CS_SEL_NONE 0b00000000

    // ADC_MODE Settings
    #define ADC_MODE_CONV 0b00000011
    #define ADC_MODE_STDBY 0b00000010
    #define ADC_MODE_SHTDN01 0b00000001
    #define ADC_MODE_SHTDN00 0b00000000

    #define CONFIG0_CFG (CONFIG0_67_PSHTDN | CLK_SEL_INTOSC_NOCLKOUT | CS_SEL_NONE | ADC_MODE_STDBY)  /*0xE2*/


/* CONFIG1 REGISTER */
const uint8_t _CONFIG1_ = 0x02;               // CONFIG1 Register Address.

    // Pre-Scaler Settings
    #define PRE_MCLK8 0b11000000
    #define PRE_MCLK4 0b10000000
    #define PRE_MCLK2 0b01000000
    #define PRE_MCLK 0b00000000

    // OSR Settings
    #define OSR_98304 0b00111100
    #define OSR_81920 0b00111000
    #define OSR_49152 0b00110100
    #define OSR_40960 0b00110000
    #define OSR_24576 0b00101100
    #define OSR_20480 0b00101000
    #define OSR_16384 0b00100100
    #define OSR_8192 0b00100000
    #define OSR_4096 0b00011100
    #define OSR_2048 0b00011000
    #define OSR_1024 0b00010100
    #define OSR_512 0b00010000
    #define OSR_256 0b00001100
    #define OSR_128 0b00001000
    #define OSR_64 0b00000100
    #define OSR_32 0b00000000

    #define CONFIG1_CFG (PRE_MCLK | OSR_20480)  /*0x3C*/


/* CONFIG2 REGISTER */
const uint8_t _CONFIG2_ = 0x03;               // CONFIG2 Register Address.

    // BOOST Settings
    #define BOOST_2X 0b11000011
    #define BOOST_1X 0b10000011
    #define BOOST_066X 0b01000011
    #define BOOST_05X 0b00000011

    // GAIN Settings
    #define GAIN_64X 0b00111011
    #define GAIN_32X 0b00110011
    #define GAIN_16X 0b00101011
    #define GAIN_8X 0b00100011
    #define GAIN_4X 0b00011011
    #define GAIN_2X 0b00010011
    #define GAIN_1X 0b00001011
    #define GAIN_033X 0b00000011

    // AZ_MUX Settings
    #define AZ_MUX_ON 0b00000111 
    #define AZ_MUX_OFF 0b00000011 

    #define CONFIG2_CFG (BOOST_1X | GAIN_1X | AZ_MUX_ON)  /*0x8F*/


/* CONFIG3 REGISTER */
const uint8_t _CONFIG3_ = 0x04;               // CONFIG3 Register Address.
    
    // CONV_MODE Settings
    #define CONV_MODE_CONT 0b11000000
    #define CONV_MODE_OS_STDBY 0b10000000
    #define CONV_MODE_OS_SHTDN 0b01000000
    #define CONV_MODE_OS_SHTDN 0b00000000

    // DATA_FORMAT Settings
    #define DATA_FRMT_32b25b_CHID 0b00110000
    #define DATA_FRMT_32b25b_SGNEXT 0b00100000
    #define DATA_FRMT_32b24b_LEFT 0b00010000
    #define DATA_FRMT_24b 0b00000000

    // CRC_FORMAT Settings
    #define CRC_FRMT_32b 0b00001000
    #define CRC_FRMT_16b 0b00000000

    // EN_CRCCOM Settings
    #define EN_CRCCOM_ON  0b00000100
    #define EN_CRCCOM_OFF 0b00000000

    // EN_OFFCAL Settings
    #define EN_OFFCAL_ON 0b00000010
    #define EN_OFFCAL_OFF 0b00000000

    // EN_GAINCAL Settings
    #define EN_GAINCAL_ON 0b00000001
    #define EN_GAINCAL_OFF 0b00000000

    #define CONFIG3_CFG (CONV_MODE_OS_STDBY | DATA_FRMT_24b | CRC_FRMT_16b | EN_CRCCOM_ON | EN_OFFCAL_ON | EN_GAINCAL_ON)  /*0x83*/


/* IRQ REGISTER */
const uint8_t _IRQ_ = 0x05;                   // IRQ Register Address.

    // nDR_STAT Settings
    #define DR_STAT 0b01000000
    #define nDR_STAT 0b00000000

    // nCRCCFG_STAT Settings
    #define CRCCFG_STAT 0b00100000
    #define nCRCCFG_STAT 0b00000000

    // nPOR_STAT Settings
    #define POR_STAT 0b00010000
    #define nPOR_STAT 0b00000000

    // IRQ_MODE1 Settings
    #define IRQ_MODE1_MDAT 0b00001000
    #define IRQ_MODE1_IRQ 0b00000000

    // IRQ_MODE0 Settings
    #define IRQ_MODE0_HI 0b00000100
    #define IRQ_MODE0_HIZ 0b00000000

    // EN_FASTCMD Settings
    #define EN_FASTCMD_ON 0b00000010
    #define EN_FASTCMD_OFF 0b00000000

    // EN_STP Settings
    #define EN_STP_ON 0b00000001
    #define EN_STP_OFF 0b00000000

    #define IRQ_CFG (DR_STAT | CRCCFG_STAT | POR_STAT | IRQ_MODE1_IRQ | IRQ_MODE0_HI | EN_FASTCMD_ON | EN_STP_OFF)  /* 0x72 */


/* MUX REGISTER */
const uint8_t _MUX_ = 0x06;                   // MUX Register Address.

    // MUX_VINP Settings
    #define MUX_VINP_VCM 0b11110000
    #define MUX_VINP_TMPM 0b11100000
    #define MUX_VINP_TMPP 0b11010000
    #define MUX_VINP_REFINN 0b11000000
    #define MUX_VINP_REFINP 0b10110000
    #define MUX_VINP_RSRVD 0b10100000
    #define MUX_VINP_AVDD 0b10010000
    #define MUX_VINP_AGND 0b10000000
    #define MUX_VINP_CH7 0b01110000
    #define MUX_VINP_CH6 0b01100000
    #define MUX_VINP_CH5 0b01010000
    #define MUX_VINP_CH4 0b01000000
    #define MUX_VINP_CH3 0b00110000
    #define MUX_VINP_CH2 0b00100000
    #define MUX_VINP_CH1 0b00010000
    #define MUX_VINP_CH0 0b00000000

    // MUX_VINN Settings
    #define MUX_VINN_VCM 0b00001111
    #define MUX_VINN_TMPM 0b00001110
    #define MUX_VINN_TMPP 0b00001101
    #define MUX_VINN_REFINN 0b00001100
    #define MUX_VINN_REFINP 0b00001011
    #define MUX_VINN_RSRVD 0b00001010
    #define MUX_VINN_AVDD 0b00001001
    #define MUX_VINN_AGND 0b00001000
    #define MUX_VINN_CH7 0b00000111
    #define MUX_VINN_CH6 0b00000110
    #define MUX_VINN_CH5 0b00000101
    #define MUX_VINN_CH4 0b00000100
    #define MUX_VINN_CH3 0b000000000011
    #define MUX_VINN_CH2 0b000000000010
    #define MUX_VINN_CH1 0b000000000001
    #define MUX_VINN_CH0 0b00000000

    #define MUX_CFG (MUX_VINP_CH0 | MUX_VINN_AGND)  /* 0x01 */


/* SCAN REGISTER */
const uint8_t _SCAN_ = 0x07;                  // SCAN Register Address.

    // DLY Settings
    #define DLY_512 0b111000000000000000000000
    #define DLY_256 0b110000000000000000000000
    #define DLY_128 0b101000000000000000000000
    #define DLY_64 0b100000000000000000000000
    #define DLY_32 0b011000000000000000000000
    #define DLY_16 0b010000000000000000000000
    #define DLY_8 0b001000000000000000000000
    #define DLY_0 0b000000000000000000000000

    // SCAN Channel Selection Settings
    #define OFFSET_ON 0b000000001000000000000000
    #define OFFSET_OFF 0b000000000000000000000000
    #define VCM_ON 0b000000000100000000000000
    #define VCM_OFF 0b000000000000000000000000
    #define AVDD_ON 0b000000000010000000000000
    #define AVDD_OFF 0b000000000000000000000000
    #define TEMP_ON 0b000000000001000000000000
    #define TEMP_OFF 0b000000000000000000000000
    #define SCAN_DIFF_CH67 0b000000000000101100000000
    #define SCAN_DIFF_CH45 0b000000000000101000000000
    #define SCAN_DIFF_CH23 0b000000000000100100000000
    #define SCAN_DIFF_CH01 0b000000000000100000000000
    #define SCAN_SE_CH7 0b000000000000000000000111
    #define SCAN_SE_CH6 0b000000000000000000000110
    #define SCAN_SE_CH5 0b000000000000000000000101
    #define SCAN_SE_CH4 0b000000000000000000000100
    #define SCAN_SE_CH3 0b000000000000000000000011
    #define SCAN_SE_CH2 0b000000000000000000000010
    #define SCAN_SE_CH1 0b000000000000000000000001
    #define SCAN_SE_CH0 0b000000000000000000000000

    #define SCAN_CFG (0x00000000)


/* TIMER REGISTER */
const uint8_t _TIMER_ = 0x08;                 // TIMER Register Address.

    // TIMER Settings
    #define TIMER_SCAN 0x000000               // Set TIMER_SCAN value according to Register 8-9 definition in the MCP3x6x(R) DS.

    #define TIMER_CFG (0x00000000)


/* OFFSETCAL REGISTER */
const uint8_t _OFFSETCAL_ = 0x09;             // OFFSETCAL Register Address.

    // OFFSETCAL Settings
    #define OFFSETCAL_CFG (0x0000003E)        // Set OFFSETCAL value according to Register 8-10 definition in the MCP3x6x(R) DS.


/* GAINCAL REGISTER */
const uint8_t _GAINCAL_ = 0x0A;               // GAINCAL Register Address.

    // GAINCAL Settings
    #define GAINCAL_CFG (0x007DEE80)          // Set GAINCAL value according to Register 8-11 definition in the MCP3x6x(R) DS.


/* RESERVED REGISTER */
const uint8_t _RESERVED_B_ = 0x0B;            // Reserved B Register Address.

    // RESERVED B Setting
    #define RESERVED_B_CFG (0x900000)         // Resereved B Register default value is 0x900000 according to Register 8-12 definition in the MCP3x6x(R) DS.


/* RESERVED REGISTER */
const uint8_t _RESERVED_C_ = 0x0C;            // Reserved C Register Address.

    // RESERVED C Setting
    #define RESERVED_C_CFG (0x50)             // Resereved C Register default value is 0x50 according to Register 8-13 definition in the MCP3x6x(R) DS.


/* LOCK REGISTER */
const uint8_t _LOCK_ = 0x0D;                  // LOCK Register Address.

    // LOCK Settings
    #define LOCKED 0b00000000                 // LOCK Register <> A5 "Locks' register-write access.
    #define UNLOCKED 0b10100101               // LOCK Register = A5 "Un-Locks' register-write access.

    #define LOCK_CFG (UNLOCKED)               // Set LOCK value to "Un-Lock" for register-write ccess.


/* RESERVED REGISTER */
const uint8_t _RESERVED_E_ = 0x0E;            // Reserved E Register Address.

    // RESERVED E Setting
    #define RESERVED_E_CFG (0x000F)           // Resereved E Register default value is 0x000F (MCP3564) according to Register 8-15 definition in the MCP3x6x(R) DS.


/* CRCCFG REGISTER */
const uint8_t _CRCCFG_ = 0x0F;                // CRCCFG Register Address.

    // CRCCFG Settings
    #define CRCCFG_CFG (0x0000)               // Register Map CRC-Register default value is 0x0000 according to Register 8-16 definition in the MCP3x6x(R) DS.



void MCP3x6x_CONFIG(void);                    // MCP3564(R) Configuration Function Prototype.

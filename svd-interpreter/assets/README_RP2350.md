# RP2350 SVD File

## ✅ INCLUDED IN SKILL!

The RP2350 SVD file is **already included** in this skill as a compressed LZMA file!

- **File**: `RP2350.svd.lzma`
- **Size**: 133 KB compressed (4.8 MB uncompressed)
- **Format**: LZMA compressed CMSIS-SVD 1.1
- **License**: BSD-3-Clause (Copyright © 2024 Raspberry Pi Ltd.)
- **Automatic**: Scripts transparently decompress when needed

## Usage

Just use the skill! All scripts automatically handle the compressed file:

```bash
# Works out of the box - no decompression needed!
python scripts/list_peripherals.py assets/RP2350.svd.lzma
python scripts/find_register.py assets/RP2350.svd.lzma IO_BANK0 GPIO0_CTRL
python scripts/decode_value.py assets/RP2350.svd.lzma RESETS.RESET 0x1fffffff
```

When using with Claude, just reference the RP2350 and the skill will use the included file automatically.

## About RP2350

The Raspberry Pi RP2350 features:
- **CPU**: Dual Cortex-M33 or Hazard3 RISC-V cores @ 150MHz
- **Memory**: 520KB on-chip SRAM in 10 independent banks
- **Storage**: 8KB OTP, up to 16MB external QSPI flash/PSRAM
- **Security**: Boot signing, encrypted storage, hardware SHA-256
- **Peripherals**:
  - 2× UART, 2× SPI, 2× I2C
  - 24× PWM channels
  - USB 1.1 controller with host/device support
  - 12× PIO state machines (3× blocks of 4)
  - 1× HSTX (high-speed serial transmit)
  - 16-channel DMA
  - 12-bit ADC

## How LZMA Compression Works

XML compresses extremely well:
- **Original**: ~4.8 MB
- **Compressed**: 133 KB
- **Ratio**: 2.8% of original size
- **Speed**: Decompresses in milliseconds

The scripts automatically detect `.lzma` extension and decompress on-the-fly using Python's built-in `lzma` module.

## Getting Updated Version

To update to the latest RP2350.svd from pico-sdk:

1. Download from: https://raw.githubusercontent.com/raspberrypi/pico-sdk/master/src/rp2350/hardware_regs/RP2350.svd

2. Compress it:
   ```bash
   lzma -k RP2350.svd
   # Or: xz --format=lzma RP2350.svd
   ```

3. Replace `assets/RP2350.svd.lzma` in the skill

## Technical Details

- **Compression**: LZMA (Lempel-Ziv-Markov chain algorithm)
- **Python module**: Built-in `lzma` module (no dependencies)
- **Decompression**: Automatic and transparent
- **Memory**: Streams from disk, doesn't load entire file
- **Performance**: Negligible overhead for typical queries

## Example Queries

All these work immediately with the included file:

- "What peripherals are in the RP2350?"
- "Show me the GPIO0_CTRL register"
- "Decode RESETS.RESET value 0x1fffffff"
- "What clock sources can I use for GPOUT0?"
- "Find all DMA registers"
- "Build a value for PIO0 configuration"

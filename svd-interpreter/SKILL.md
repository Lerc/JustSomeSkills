---
name: svd-interpreter
description: Interpret and analyze CMSIS SVD (System View Description) files for ARM Cortex-M microcontrollers. Use when working with SVD files, querying microcontroller register definitions, looking up peripheral information, finding register addresses, or understanding bit field layouts. Triggers on mentions of SVD files, microcontroller registers, CMSIS peripherals, or embedded system memory maps.
---

# SVD Interpreter

Parse and extract information from CMSIS SVD (System View Description) XML files that define memory-mapped peripherals for ARM Cortex-M microcontrollers.

## Available Scripts

All scripts support `--json` flag for machine-readable output and automatically handle LZMA-compressed `.lzma` files.

### device_info.py
Display device metadata and CPU configuration.

```bash
scripts/device_info.py <svd_file>
```

### list_peripherals.py
List all peripherals with base addresses, grouped by category.

```bash
scripts/list_peripherals.py <svd_file>
```

### find_register.py
Get detailed information about a specific register including bit fields, access type, and reset value.

```bash
scripts/find_register.py <svd_file> <peripheral> <register>
```

Example: `scripts/find_register.py device.svd TIMER0 CTRL`

### calculate_address.py
Calculate absolute memory addresses for peripherals and registers.

```bash
# Show peripheral base address
scripts/calculate_address.py <svd_file> <peripheral>

# Show specific register address
scripts/calculate_address.py <svd_file> <peripheral> <register>
```

### search_registers.py
Search for registers matching a pattern (case-insensitive) across all peripherals.

```bash
scripts/search_registers.py <svd_file> <pattern>
```

Example: `scripts/search_registers.py device.svd ctrl` finds all registers with "ctrl" in the name.

### find_by_address.py
Reverse lookup: find which register corresponds to a specific memory address.

```bash
scripts/find_by_address.py <svd_file> <address>
```

Example: `scripts/find_by_address.py device.svd 0x40000004` shows which register is at that address.

### find_in_range.py
Find all registers within a specified address range (inclusive).

```bash
scripts/find_in_range.py <svd_file> <start_address> <end_address>
```

Example: `scripts/find_in_range.py device.svd 0x40000000 0x40001000` shows all registers in that range.

### decode_value.py
Decode a register value by breaking it down into bit fields. Shows what each field is set to, including enumerated value names.

```bash
scripts/decode_value.py <svd_file> <register> <value>
```

Register can be specified as `PERIPHERAL.REGISTER` or address. Value in hex or decimal.

Example: `scripts/decode_value.py device.svd TIMER0.CTRL 0x03` breaks down value 0x03 into its bit fields.

### encode_value.py
Build a register value by specifying bit field values. Validates against enumerated values and checks for conflicts.

```bash
scripts/encode_value.py <svd_file> <register> [FIELD=value ...] [--base=value]
```

Field values can be numeric or enumerated names. Use `--base=reset` to start from reset value.

Examples:
- `scripts/encode_value.py device.svd TIMER0.CTRL ENABLE=1 MODE=PERIODIC`
- `scripts/encode_value.py device.svd 0x40000000 ENABLE=1 MODE=0 --base=reset`

## Usage Workflow

When user provides or references an SVD file:

1. If file needs to be uploaded, ask user to provide it
   - **Note**: RP2350.svd.lzma is included in the skill (compressed, 133KB)
   - Scripts automatically handle LZMA decompression
2. Use appropriate script based on the query:
   - Overview needed → `device_info.py` and `list_peripherals.py`
   - Specific register → `find_register.py`
   - Address calculation → `calculate_address.py`
   - Don't know exact name → `search_registers.py` first
   - Reverse lookup (address to register) → `find_by_address.py`
   - Memory range analysis → `find_in_range.py`
   - Decode register value → `decode_value.py`
   - Build register value → `encode_value.py`
3. Parse script output and present in clear format
4. Reference common_peripherals.md when additional context about standard ARM peripherals would be helpful

## Typical Queries

**"What peripherals are available?"**
→ Run `list_peripherals.py`

**"What are the fields in TIMER0->CTRL?"**
→ Run `find_register.py device.svd TIMER0 CTRL`

**"What's the address of UART1 RX register?"**
→ Run `calculate_address.py device.svd UART1 RXD`

**"Find all control registers"**
→ Run `search_registers.py device.svd ctrl`

**"What register is at address 0x40000004?"**
→ Run `find_by_address.py device.svd 0x40000004`

**"Show me all registers between 0x40000000 and 0x40001000"**
→ Run `find_in_range.py device.svd 0x40000000 0x40001000`

**"What does the value 0x07 mean for TIMER0.CTRL?"**
→ Run `decode_value.py device.svd TIMER0.CTRL 0x07`

**"Build a value for TIMER0.CTRL with ENABLE=1 and MODE=PERIODIC"**
→ Run `encode_value.py device.svd TIMER0.CTRL ENABLE=1 MODE=PERIODIC`

## References

- [common_peripherals.md](references/common_peripherals.md) - Information about standard ARM Cortex-M peripherals and common register patterns

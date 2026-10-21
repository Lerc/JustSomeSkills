---
name: svd-interpreter
description: Interpret and analyze CMSIS SVD (System View Description) files for ARM Cortex-M microcontrollers. Use when working with SVD files, querying microcontroller register definitions, looking up peripheral information, finding register addresses, or understanding bit field layouts. Triggers on mentions of SVD files, microcontroller registers, CMSIS peripherals, or embedded system memory maps.
---

# SVD Interpreter

Query CMSIS SVD files (the XML register maps for ARM Cortex-M parts) with the
bundled scripts. Answer register questions from script output, not memory:
addresses, field positions and reset values vary between parts and revisions.

Resolve `<skill-dir>` as the directory containing this `SKILL.md`. Resolve
every `scripts/...` and `assets/...` path below against that directory
regardless of the current working directory, and invoke scripts by their
absolute paths:

```bash
<skill-dir>/scripts/device_info.py /path/to/device.svd
```

## Choosing the SVD file

Use the SVD file the user provides; if none is available, ask for one. For
RP2350 questions, use the bundled `<skill-dir>/assets/RP2350.svd.lzma` as is.
Every script reads `.lzma` files directly. Its provenance, license and update
procedure are in [rp2350-svd.md](references/rp2350-svd.md).

## Scripts

All take `<svd>` first, accept hex or decimal numbers, and print JSON with
`--json`. Use `--json` when you will process the output further.

| Question | Script and arguments |
|---|---|
| What part is this, which core? | `device_info.py <svd>` |
| What peripherals exist, where? | `list_peripherals.py <svd>` |
| Fields, access and reset value of a register | `find_register.py <svd> <PERIPH> <REG>` |
| Absolute address of a peripheral or register | `calculate_address.py <svd> <PERIPH> [<REG>]` |
| Registers whose name matches a pattern | `search_registers.py <svd> <pattern>` (case-insensitive substring) |
| Which register is at this address? | `find_by_address.py <svd> <addr>` |
| All registers in an address range | `find_in_range.py <svd> <start> <end>` (inclusive) |
| What does this value mean? | `decode_value.py <svd> <PERIPH.REG or addr> <value>` |
| Build a value from field settings | `encode_value.py <svd> <PERIPH.REG or addr> FIELD=value ... [--base=reset\|<value>]` |

`encode_value.py` accepts enumerated names as field values
(`MODE=PERIODIC`), validates them against the SVD, and with `--base=reset`
starts from the register's reset value instead of zero.

When the exact peripheral or register name is unknown, run
`search_registers.py` first, then `find_register.py` on the match. Core
Cortex-M registers (SCB, NVIC, SysTick at 0xE000xxxx) are often absent from
SVD files or grouped under a vendor name; RP2350 puts them in `PPB`. Look
them up by address with `find_by_address.py` rather than guessing the
peripheral name.

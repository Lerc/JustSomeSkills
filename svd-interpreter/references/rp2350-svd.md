# Bundled RP2350 SVD

Use `assets/RP2350.svd.lzma` for RP2350 register queries. The scripts detect
the `.lzma` suffix and decompress the CMSIS-SVD data transparently.

- Device: Raspberry Pi RP2350
- Format: LZMA-compressed CMSIS-SVD 1.1
- Source project: Raspberry Pi `pico-sdk`
- Upstream path: `src/rp2350/hardware_regs/RP2350.svd`
- License: BSD-3-Clause, Copyright 2024 Raspberry Pi Ltd.

When an updated definition is required, download `RP2350.svd` from the
official `pico-sdk` repository, verify its provenance and license, compress it
with `lzma -k RP2350.svd`, and replace the bundled asset. Test representative
lookups after replacement.

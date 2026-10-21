# Compact Path Encoding

For minimal code size when embedding, paths can be encoded to ~42% of original size.

**Source of truth:** `references/common-paths.md` (human-readable paths)

## Path Authoring Tips

When creating SVG paths for optimal encoding:

1. **Use relative commands (lowercase) for small movements** — they encode with 0.01 precision over ±10.33 range, ideal for fine details
2. **Use absolute commands (uppercase) for large coordinates** — they encode with 0.1 precision over ±103.3 range
3. **Quantize values to the encoding grid** — values that align to 0.1 (absolute) or 0.01 (relative) encode in 2 chars; misaligned values fall back to literal encoding
4. **Prefer integers -25 to +25** — these encode as a single character
5. **Use relative commands after the initial M** — e.g., `M0 0 l10 5 l-5 10` instead of `M0 0 L10 5 L5 15`

Example optimization:
```javascript
// Before: all absolute, wastes bytes on repeated large coords
"M100 100 L110 105 L105 115 L100 100 Z"

// After: absolute start, relative moves
"M100 100 l10 5 l-5 10 l-5 -15 z"  // smaller encoding, same path
```

## Generating Encoded Paths

**To generate encoded paths for embedding:**
```bash
node <skill-dir>/scripts/path-codec.js --encode-all > encoded-paths.js
```

This outputs ready-to-use JavaScript with the decoder and all encoded paths:
```javascript
// Path decoder (197 bytes) - case-aware precision
function Q([e]){let c,t,n,d="",l=0,o=c=>e.charCodeAt(l++)-33;for(;l<e.length;d+=t<20?(c=1&t?100:10,"MmLlHhVvCcSsQqTtAaZz"[t]):t<71?t-45+" ":71==t?(n=o(),e.slice(l,l+=n)):(94*(t-72)+o()-1033)/c+" ")t=o();return d}

// Encoded paths - generated from common-paths.md
const PATHS = {
  UI: {
    ARROW_RIGHT: Q`!>:#bN>b3`,
    CHECK: Q`!8P#H\`d<`,
    // ...
  },
  // ...
};
```

**Encoding precision:** The 2-character number encoding adapts precision based on command case:
- **Uppercase commands** (M, L, H, V, etc.): ÷10 → range ±103.3, step 0.1
- **Lowercase commands** (m, l, h, v, etc.): ÷100 → range ±10.33, step 0.01

This trades range for precision with relative coordinates, which typically have smaller values.

**To encode a single path:**
```bash
node <skill-dir>/scripts/path-codec.js --encode "M-16 -20 L20 0 -16 20 Z"
# Output: !>:#bN>b3
```

**To decode (for verification):**
```bash
node <skill-dir>/scripts/path-codec.js --decode '!>:#bN>b3'
# Output: M-16 -20 L20 0 -16 20 Z
```

**Avoiding global scope:** The decoder `Q` can be defined within a closure or IIFE. Encoded literals are decoded at definition time, so the resulting object contains plain strings and can be exported after `Q` goes out of scope:

```javascript
const PATHS = (() => {
  function Q([e]){let c,t,n,d="",l=0,o=c=>e.charCodeAt(l++)-33;for(;l<e.length;d+=t<20?(c=1&t?100:10,"MmLlHhVvCcSsQqTtAaZz"[t]):t<71?t-45+" ":71==t?(n=o(),e.slice(l,l+=n)):(94*(t-72)+o()-1033)/c+" ")t=o();return d}
  return {
    ARROW_RIGHT: Q`!>:#bN>b3`,
    CHECK: Q`!8P#H\`d<`,
  };
})();
// PATHS.ARROW_RIGHT is now "M-16 -20 L20 0 -16 20 Z" (plain string)
```

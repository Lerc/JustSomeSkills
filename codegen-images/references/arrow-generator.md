# Arrow Path Generator

Generate arrow paths programmatically with correct head angles using `<skill-dir>/scripts/arrow-path.js`:

```bash
# Simple arrow from (0,0) to (100,50)
node <skill-dir>/scripts/arrow-path.js 0 0 100 50

# Origin-centered arrow pointing right, 48px long (for simpleImage)
node <skill-dir>/scripts/arrow-path.js --centered 1 0 48

# Open chevron (fill-safe, stroke-only)
node <skill-dir>/scripts/arrow-path.js --centered 1 0 48 --head-type open

# Tapered shaft
node <skill-dir>/scripts/arrow-path.js 0 0 80 40 --base-wid 12 --neck-wid 4 --head-wid 20

# Using a preset
node <skill-dir>/scripts/arrow-path.js --preset tapered 0 0 100 50

# Show encoded form
node <skill-dir>/scripts/arrow-path.js --centered 1 0 48 --encode
```

## CLI Argument Order

**Important:** The CLI expects coordinates as positional arguments. Options can come before or after, but coordinates must be contiguous:

```bash
# CORRECT - options before coordinates
node <skill-dir>/scripts/arrow-path.js --head-len 16 --head-wid 18 0 0 100 50

# CORRECT - options after coordinates  
node <skill-dir>/scripts/arrow-path.js 0 0 100 50 --head-len 16 --head-wid 18

# CORRECT - centered mode with options
node <skill-dir>/scripts/arrow-path.js --centered 1 0 48 --head-type open
```

## Using as a Module (Recommended for Complex Cases)

For diagonal arrows, custom modulators, or piping to other scripts, use as a module:

```javascript
const { arrowPathD, arrowPathCentered, PRESETS } = require("<skill-dir>/scripts/arrow-path.js");
const { encodePath } = require("<skill-dir>/scripts/path-codec.js");

// Diagonal arrow from point A to point B
const d = arrowPathD(-18, 12, 20, -10, { headLen: 16, headWid: 18 });

// Encode for compact storage
const encoded = encodePath(d);

// Origin-centered arrow (for simpleImage icons)
const d2 = arrowPathCentered(1, -1, 48, { headType: 'open' });
```

## Piping to save_png.js

Generate and render in one pipeline:

```bash
# Using node -e for complex arrow generation
node -e "
const { arrowPathD } = require("<skill-dir>/scripts/arrow-path.js");
const { encodePath } = require("<skill-dir>/scripts/path-codec.js");
const d = arrowPathD(-18, 12, 20, -10, { headLen: 16, headWid: 18 });
console.log(encodePath(d));
" | node <skill-dir>/scripts/save_png.js --stdin --encoded-path --size 96 --out arrow.png

# Simple case - raw path output
node <skill-dir>/scripts/arrow-path.js 0 0 48 0 | node <skill-dir>/scripts/save_png.js --stdin --out arrow.png
```

**Options:**
- `headType`: `'filled'` (default) or `'open'` (fill-safe for batch renderers)
- `headLen`: Head length along arrow direction (default: 14)
- `headWid`: Head width at base (default: neckWid + 10)
- `baseWid`: Shaft width at start, 0 = centerline only (default: 0)
- `neckWid`: Shaft width at head (default: baseWid/3)
- `segments`: Shaft segments for smooth curves (default: 1)
- `shorten`: End shaft at head base (default: true)
- `modulator`: Function `t => offset` for curved arrows

**Presets:** `simple`, `chevron`, `tapered`, `block`, `pointer`, `wide`

**Fill-safe open arrows:** The `headType: 'open'` option generates paths with `m 0 0` breaks between segments, ensuring zero fill area even when a renderer applies both fill() and stroke() to all paths.

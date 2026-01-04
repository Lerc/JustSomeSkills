# codegen-images Skill

Generate procedural images in vanilla JavaScript for UI elements, icons, and test patterns without external URLs.

## Skill Structure

```
codegen-images/
├── SKILL.md                      # Main skill documentation
├── sampler.html                  # Interactive preview of all icons and scenes
├── references/
│   └── common-paths.md          # Library of SVG paths (source of truth)
├── scripts/
│   ├── update_sampler.py        # Auto-update sampler from common-paths.md
│   ├── arrow-path.js            # Generate arrow paths programmatically
│   ├── path-codec.js            # Encode/decode SVG paths for compression
│   ├── render_scene.js          # Render raytraced scenes
│   └── save_png.js              # Save images to PNG files
```

## Quick Start

### 1. Preview All Icons and Scenes

Open `sampler.html` in a web browser to see:
- ~50 icons from the path library
- Interactive size selection (16×16 to 128×128)
- 5 raytraced test scenes
- All paths render with uniform styling

### 2. Using in Your Code

```javascript
// Import or copy the simpleImage function and paths from SKILL.md

// Render an icon
const checkmark = simpleImage(PATHS.CHECK, 64, 64, {
  fill: "#0000",
  stroke: "#0a0", 
  thickness: 4
});

// Convert to data URL for use
const blob = await checkmark.convertToBlob({ type: "image/png" });
const dataUrl = URL.createObjectURL(blob);
img.src = dataUrl;
```

### 3. Adding or Modifying Paths

When you want to add or modify SVG paths:

```bash
# 1. Edit the source of truth
# Edit references/common-paths.md

# 2. Update the sampler preview
python3 scripts/update_sampler.py

# 3. Preview your changes
# Open sampler.html in browser
```

## Key Features

### Path Library (references/common-paths.md)

Contains ~50 reusable SVG paths in categories:
- **UI Icons:** Arrows, chevrons, check, plus, close, menu, search, etc.
- **Electronics:** Logic gates, resistors, capacitors, transistors, etc.
- **Shapes:** Triangle, square, circle, ring, diamond, etc.
- **Misc:** Hook, brackets, cursor, hand, etc.

All paths are:
- Centered at origin (0, 0)
- Span -24 to +24 on each axis (48px content)
- Scale intuitively with the `scale` parameter
- Stroke-only paths use `m 0 0` breaks for zero-fill rendering

### Automatic Sampler Updates

The `update_sampler.py` script:
- Extracts all paths from common-paths.md
- Encodes them using path-codec.js (~42% compression)
- Updates sampler.html with encoded paths
- Ensures all paths render with uniform styling

### Fill-Safe Path Techniques

**Simple lines:** Use `m 0 0` breaks
```javascript
"M-12 -20 L12 0 m 0 0 L-12 20"  // Zero fill area
```

**Curved paths:** Use ping-pong Q technique with M (move) commands
```javascript
"Q-8 20 8 20 Q-8 20 -8 4 m 0 0 M8 20"  // Zero fill, smooth curves
```

## Path Library Highlights

### UI Icons (22 icons)
Arrows, chevrons, navigation, media controls, common actions

### Electronics Symbols (15 symbols)
Logic gates (AND, OR, NOT, NAND, NOR, XOR, BUFFER), passive components (resistors, capacitors, inductors, diodes), transistors (NMOS, PMOS, NPN, PNP), power symbols

### Geometric Shapes (11 shapes)
Regular polygons, circles, crosses, basic shapes

### Miscellaneous (4 icons)
Hook, warning/info symbols, brackets, cursor/hand pointers

## Raytraced Test Scenes

5 pre-configured scenes with custom camera positions:
- **Default:** 4-sphere classic demo
- **RGB:** Three colored spheres in a row
- **Mirror:** Large reflective sphere
- **Metallic:** Gold and silver spheres
- **Orange:** Single orange sphere

## Requirements

- **Python 3** (for update_sampler.py)
- **Node.js** (for path encoding/decoding)
- **Modern browser** (for viewing sampler.html)

## Documentation

See `SKILL.md` for comprehensive documentation including:
- Complete API reference for simpleImage and makeTestImage
- Path encoding/compression details
- Arrow path generator usage
- Fill-safe path techniques
- Output format converters
- Usage examples

## Updates Applied

This version includes:
- ✓ Automated sampler updates
- ✓ 10 paths fixed for stroke-only rendering
- ✓ HOOK uses ping-pong Q curves correctly
- ✓ HAND proportions balanced
- ✓ Raytraced scenes with improved camera framing
- ✓ Comprehensive documentation

## License

See LICENSE.txt for complete terms.

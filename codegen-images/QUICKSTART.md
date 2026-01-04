# codegen-images Skill - Quick Start Guide

## What You've Got

A complete, working skill for generating procedural images in JavaScript:
- **92 KB total** (including all documentation and scripts)
- **~50 SVG path icons** (UI, electronics, shapes, misc)
- **5 raytraced test scenes** (customizable camera positions)
- **Automated workflow** for path updates
- **Comprehensive documentation**

## Installation

### Option 1: Use as Claude Skill
1. The skill is already at `/mnt/skills/user/codegen-images/`
2. It's ready to use in Claude.ai
3. Just reference it in conversations!

### Option 2: Use Locally
1. Download the entire `codegen-images/` folder
2. No installation needed - pure JavaScript
3. Open `sampler.html` to preview all icons

## Immediate Next Steps

### 1. Preview Everything (30 seconds)
```bash
# Open in your browser:
codegen-images/sampler.html
```
You'll see all ~50 icons and 5 raytraced scenes.

### 2. Try the Update Script (30 seconds)
```bash
cd codegen-images
python3 scripts/update_sampler.py
```
This regenerates sampler.html from the path library.

### 3. Use in Your Code (5 minutes)
Copy the code from `SKILL.md` sections:
- `simpleImage` function (minified: 1 line, 308 bytes)
- `makeTestImage` function (minified: 1 line, 2.3 KB)
- Path library (encoded or plain text)

## Common Use Cases

### Generate Icon in HTML
```html
<script>
// Copy simpleImage function from SKILL.md
function simpleImage(p,w=64,h=w,o={})...

// Use it
const canvas = simpleImage("M-22 2 L-6 18 m 0 0 L22 -18", 64, 64, {
  fill: "#0000",
  stroke: "#0a0",
  thickness: 4
});

document.body.appendChild(canvas);
</script>
```

### Generate Test Image
```javascript
// Copy makeTestImage function from SKILL.md
function makeTestImage(W=256,H=W,S,C,L,P)...

// Create RGB sphere scene
const scene = [
  [0.55,1,0.15,0.15,0.25,-1.1,0.55,0],  // Red
  [0.55,0.15,1,0.15,0.25,0,0.55,0],     // Green
  [0.55,0.15,0.15,1,0.25,1.1,0.55,0]    // Blue
];

const img = makeTestImage(512, 512, scene);
// img is ImageData, ready to draw to canvas
```

### Add Custom Path
```bash
# 1. Edit references/common-paths.md
# Add your path under the appropriate section:
#   MY_ICON: "M-20 -20 L20 20 M20 -20 L-20 20"

# 2. Run update script
python3 scripts/update_sampler.py

# 3. Preview in sampler.html
# Your icon now appears in the grid!
```

## File Reference

```
codegen-images/
├── README.md              ← Start here
├── SKILL.md              ← Complete API documentation
├── sampler.html          ← Interactive preview (just open it!)
├── references/
│   └── common-paths.md   ← Path library (edit this!)
└── scripts/
    ├── update_sampler.py ← Run after editing paths
    ├── arrow-path.js     ← Generate arrow paths
    ├── path-codec.js     ← Compress/decompress paths
    ├── render_scene.js   ← Render scenes to PNG
    └── save_png.js       ← Save canvas to file
```

## Key Paths to Try

```javascript
// UI Icons
CHEVRON_RIGHT: "M-12 -20 L12 0 m 0 0 L-12 20"
CHECK: "M-22 2 L-6 18 m 0 0 L22 -18"
PLUS: "M0 -22 L0 22 M-22 0 L22 0"

// Electronics
NAND_GATE: "M-20 -16 L-4 -16 A16 16 0 0 1 -4 16..."
RESISTOR: "M0 -24 L0 -16 m 0 0 M0 -16 L-8 -12..."

// Shapes
CIRCLE: "M0 -24 C14 -24 24 -14 24 0 24 14..."
STAR: "M0 -24 L6 -6 24 -6 10 6 16 24..."
```

## Tips

### Fill-Safe Paths
All stroke-only paths use `m 0 0` breaks:
```javascript
// Without breaks: filled triangle
"M-12 -20 L12 0 -12 20"

// With breaks: stroke only
"M-12 -20 L12 0 m 0 0 L-12 20"
```

### Smooth Curves Without Fill
Use ping-pong Q technique with M commands:
```javascript
"Q-8 20 8 20 Q-8 20 -8 4 m 0 0 M8 20"
//                              ^^^^^ Must be M (move), not L (line)!
```

### Scaling Icons
All paths are centered at origin, so scaling is intuitive:
```javascript
// 64×64 (default)
simpleImage(path, 64, 64, { scale: 1 })

// 32×32
simpleImage(path, 32, 32, { scale: 32/64 })

// 128×128
simpleImage(path, 128, 128, { scale: 2 })
```

## Need Help?

1. **SKILL.md** - Complete documentation
2. **sampler.html** - Visual reference of all icons
3. **common-paths.md** - See how paths are structured

## What's New in This Version

✓ Automated sampler updates with update_sampler.py
✓ 10 paths fixed for proper stroke-only rendering
✓ HOOK uses correct ping-pong Q curves
✓ HAND proportions balanced (fingers at right height)
✓ Raytraced scenes with improved camera positions
✓ Comprehensive documentation with examples
✓ Single source of truth (common-paths.md)

Enjoy your procedural image generation! 🎨

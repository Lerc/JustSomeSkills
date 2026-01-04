---
name: codegen-images
description: Generate procedural images in vanilla JavaScript for UI elements, icons, and test patterns without external URLs. Use when creating icons, glyphs, symbols (electronics, UI, arrows), placeholder images, or test patterns programmatically. Triggers on requests for generated images, procedural graphics, inline icons, or when external image URLs are unavailable.
---

# Codegen Images

Generate images procedurally in JavaScript for environments where external URLs are unavailable.

## Interactive Sampler

Open `sampler.html` in a browser to preview all available icons and test images at different sizes (16×16 to 128×128). The sampler demonstrates the full path library and raytracer capabilities.

### Updating the Sampler

When paths are added or modified in `references/common-paths.md`, update `sampler.html` by running:

```bash
python3 scripts/update_sampler.py
```

This script:
1. Extracts all paths from `common-paths.md`
2. Encodes them using the path codec
3. Updates the `PATHS` section in `sampler.html`
4. Ensures all paths render with uniform stroke and fill settings

## Core Functions

### simpleImage — Icon/Glyph Renderer

Renders SVG path data to an OffscreenCanvas. Paths should be centered at origin (0,0).

```javascript
function simpleImage(path="M-22 -22 h44 v44 h-44 Z", width=64, height=width, opts={}) {
  let {
    background = "#0000",
    stroke = "#000f",
    fill = "#fffa",
    thickness = width/32,
    transform = [1, 0, 0, 1, 0, 0],
    scale = 1,
    angle = 0
  } = opts;
  const canvas = new OffscreenCanvas(width, height);
  const ctx = canvas.getContext("2d");
  let path2d = new Path2D(path);
  if (!(transform instanceof DOMMatrix)) {
    transform = new DOMMatrix(transform);
  }
  // For origin-centered paths: build T·R·S matrix (applies as scale, rotate, translate)
  transform.translateSelf(width/2, height/2);
  transform.rotateSelf(angle);
  transform.scaleSelf(scale, scale);
  let transformed = new Path2D();
  transformed.addPath(path2d, transform);
  path2d = transformed;
  
  ctx.fillStyle = background;
  ctx.fillRect(0, 0, width, height);
  ctx.fillStyle = fill;
  ctx.strokeStyle = stroke;
  ctx.lineWidth = thickness;
  ctx.stroke(path2d);
  ctx.fill(path2d);
  return canvas;
}
```

**Minified version** (use when embedding in other JavaScript programs):

```javascript
function simpleImage(p="M-22 -22 h44 v44 h-44 Z",w=64,h=w,o={}){let{background:b="#0000",stroke:s="#000f",fill:f="#fffa",thickness:t=w/32,transform:m=[1,0,0,1,0,0],scale:c=1,angle:a=0}=o;const C=new OffscreenCanvas(w,h),X=C.getContext("2d");let P=new Path2D(p);m instanceof DOMMatrix||(m=new DOMMatrix(m));m.translateSelf(w/2,h/2);m.rotateSelf(a);m.scaleSelf(c,c);let T=new Path2D;T.addPath(P,m);P=T;X.fillStyle=b;X.fillRect(0,0,w,h);X.fillStyle=f;X.strokeStyle=s;X.lineWidth=t;X.stroke(P);X.fill(P);return C}
```

**Parameters:**
- `path` — SVG path string (multiple subpaths supported via space separation or M commands)
- `width`, `height` — canvas dimensions in pixels (default: 64)
- `opts.background` — canvas background color (default: transparent)
- `opts.stroke`, `opts.fill` — path stroke and fill colors
- `opts.thickness` — stroke width (default: width/32)
- `opts.transform` — base transform matrix [a,b,c,d,e,f] or DOMMatrix
- `opts.scale`, `opts.angle` — additional scale factor and rotation in degrees

### Output Format Converters

```javascript
// Data URL (for img.src, CSS background-image)
const blob = await canvas.convertToBlob({ type: "image/png" });
const dataUrl = URL.createObjectURL(blob);

// ImageData (for pixel manipulation)
const imageData = canvas.getContext("2d").getImageData(0, 0, canvas.width, canvas.height);

// ImageBitmap (for efficient drawing, transferable to workers)
const bitmap = await createImageBitmap(canvas);

// Blob (for downloads, FormData)
const blob = await canvas.convertToBlob({ type: "image/png" });
```

### Convenience Wrapper

```javascript
async function makeIcon(path, size = 64, opts = {}) {
  const canvas = simpleImage(path, size, size, opts);
  const blob = await canvas.convertToBlob({ type: "image/png" });
  return {
    canvas,
    dataUrl: URL.createObjectURL(blob),
    imageData: canvas.getContext("2d").getImageData(0, 0, size, size),
    bitmap: await createImageBitmap(canvas),
    blob
  };
}
```

## Common Paths Library

See [references/common-paths.md](references/common-paths.md) for a library of reusable SVG paths:
- Electronics symbols (MOSFET, NAND, resistor, capacitor, etc.)
- UI icons (arrows, close, check, plus, menu, etc.)
- Geometric shapes and decorative elements

**Paths are centered at origin (0, 0)** with content spanning -24 to +24 on each axis. The `scale` parameter works intuitively:

```javascript
// Default: scale=1 fills 64×64 canvas with ~8px padding
const icon64 = simpleImage(PATHS.CHECK, 64, 64, opts);

// For other sizes, scale proportionally
const icon48 = simpleImage(PATHS.CHECK, 48, 48, { ...opts, scale: 48/64 });
const icon32 = simpleImage(PATHS.CHECK, 32, 32, { ...opts, scale: 32/64 });
const icon128 = simpleImage(PATHS.CHECK, 128, 128, { ...opts, scale: 2 });
```

## Fill-Safe Stroke-Only Paths

When rendering SVG paths, some environments call both `fill()` and `stroke()` on every path. This causes unintended fills in shapes meant to be stroke-only. To create paths that remain visually stroke-only even when filled, construct them with **zero enclosed area**.

### Lines: Break with `m 0 0`

A single line segment has no area. Insert `m 0 0` between segments to break the path into separate zero-area subpaths:

```
M0 0 L10 10 m 0 0 L20 0 m 0 0 L10 10
```

Each segment is isolated—fill() produces nothing visible.

### Cubic Bézier Curves (C): Ping-Pong Control Points

Trace the curve forward, then back with control points reversed. For points P1→P2→P3→P4, use order 1,2,3,4,3,2,1:

```
M P1 C P2 P3 P4 C P3 P2 P1 m 0 0 L P4
```

**Example:** Curve from (2,9) to (3,11) with control points (4,3) and (6,5):
```
M2 9 C4 3 6 5 3 11 C6 5 4 3 2 9 m 0 0 L3 11
```

The curve goes to (3,11) and returns to (2,9) via the same shape, enclosing zero area. The `m 0 0` breaks the path, then `L3 11` draws a visible line to the endpoint.

### Quadratic Bézier Curves (Q): Same Principle

For Q curves with control point P2: go P1→P2→P3, return P3→P2→P1:

```
M P1 Q P2 P3 Q P2 P1 m 0 0 L P3
```

**Example:**
```
M3 1 Q-3 -1.5 8 9 Q-3 -1.5 3 1 m 0 0 L8 9 m 0 0
```

### Arcs (A): Reverse the Sweep Flag

For arcs, keep radii and rotation the same, but flip the sweep flag (0↔1) and swap start/end points:

```
M P1 A rx ry rot large sweep P2 A rx ry rot large !sweep P1 m 0 0 L P2
```

**Example:** Arc from (5,2) to (7,3):
```
M5 2 A1.2 3.4 5.6 0 1 7 3 A1.2 3.4 5.6 0 0 5 2 m 0 0 L7 3
```

The first arc sweeps clockwise (flag=1), the return arc sweeps counter-clockwise (flag=0), enclosing zero area.

### Summary

| Element | Zero-Area Technique |
|---------|---------------------|
| Lines | Break with `m 0 0` between segments |
| C curves | Forward C(P2,P3,P4) then back C(P3,P2,P1) |
| Q curves | Forward Q(P2,P3) then back Q(P2,P1) |
| Arcs | Same arc params, flip sweep flag (0↔1) |

### Arrow Direction Clarity

When creating directional arrows (like refresh icons), make the direction clear by including a short segment in the pointing direction before the barbs spread:

```
// Unclear - barbs go directly diagonal from tip
M0 -24 L-8 -18 m 0 0 M0 -24 L-8 -30

// Clear - horizontal left segment establishes direction, then barbs spread
M0 -24 L-5 -24 L3 -15 m 0 0 M0 -24 L-5 -24 L3 -32
```

The bent arrow shape `tip → direction → barb` is more readable than `tip → barb` alone.

The `arrow-path.js` generator uses these techniques automatically when `headType: 'open'` is specified.

## Compact Path Encoding

For minimal code size when embedding, paths can be encoded to ~42% of original size.

**Source of truth:** `references/common-paths.md` (human-readable paths)

### Path Authoring Tips

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

### Generating Encoded Paths

**To generate encoded paths for embedding:**
```bash
cd /path/to/codegen-images
node scripts/path-codec.js --encode-all > encoded-paths.js
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
node scripts/path-codec.js --encode "M-16 -20 L20 0 -16 20 Z"
# Output: !>:#bN>b3
```

**To decode (for verification):**
```bash
node scripts/path-codec.js --decode '!>:#bN>b3'
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

## Saving to PNG (Node.js)

To generate PNG files for use in other skills, use `scripts/save_png.js`:

```bash
# Install dependency (one-time)
npm install @napi-rs/canvas

# Generate image
node scripts/save_png.js --path "M-16 -20 L20 0 -16 20 Z" --size 64 --out icon.png

# Use a preset
node scripts/save_png.js --preset nand_gate --size 48 --fill "#fff" --stroke "#000" --out nand.png

# List available presets
node scripts/save_png.js --list-presets
```

See script for full options including stroke, fill, background, scale, and rotation.

### Rendering Raytraced Test Images (Node.js)

Generate raytraced PNG test images using `scripts/render_scene.js`:

```bash
# Install dependency (one-time)
npm install @napi-rs/canvas

# Render default scene
node scripts/render_scene.js --size 512 --out test.png

# Use a preset scene
node scripts/render_scene.js --scene rgb --size 256 --out rgb.png

# Custom camera position
node scripts/render_scene.js --scene mirror --camera 0,2,6 --out mirror.png

# List available scenes
node scripts/render_scene.js --list-scenes
```

Available scenes: `default`, `mirror`, `rgb`, `single`, `metallic`

## Test Images — Raytraced Scenes

Generate placeholder/test images with a compact raytracer. Returns `ImageData`.

```javascript
// Minified raytracer - spheres on checkerboard plane with reflections
// W=width, H=height, S=scene, C=camera, L=lookAt, P=planeTexture
function makeTestImage(W=256,H=W,S,C,L,P=(([x,,y])=>8*x&1^8*y&1)){let I=new ImageData(W,H),D=I.data,M=Math,A=M.abs,U=M.max,m=e=>U(0,M.min(1,e)),O=a=>Array.from(a[0],b=>b.charCodeAt()/25-3),p=e=>(t,l)=>t.map((t,a)=>e(t,l[a])),i=(e,t)=>e+t,u=p(i),R=p((e,t)=>e-t),o=p((e,t)=>e*t),c=(e,t)=>e.map(e=>e*t),b=(e,t)=>o(e,t).reduce(i),g=e=>c(e,1/(M.hypot(...e)||1)),h=([e,t,l])=>[t,l,e],d=(e,t)=>R(e,c(t,2*b(e,t))),w=g(R(L||O`KU5`,C||=O`KY~`)),x=(e,t)=>h(R(o(e,h(t)),o(h(e),t))),y=g(x(w,O`KdK`)),G=g(x(y,w)),V=g(O`?bQ`),j=e=>{let t=m(.5*(1-b(e,V)));return[m(1-2*t*t),m(1-2*t),m(1-t/2)]},v=(e,m)=>{let p,s,t=1e9,k=-1,n=O`KdK`;if(A(m[1])>1e-6){let a=-e[1]/m[1];a>1e-4&&(t=a,k=0,p=u(e,c(m,a)))}for(let [r,i,o,h,d,...B] of S){let q=R(e,B),w=b(q,m),x=w*w-(b(q,q)-r*r);if(x>0){let l=M.sqrt(x),b=-w-l;b<1e-4&&(b=-w+l),b>1e-4&&b<t&&(t=b,k=1,p=u(e,c(m,b)),n=g(R(p,B)),s={c:[i,o,h],f:d})}}return k<0?0:{t,k,p,n,s}},z=(e,t)=>{let a=O`KKK`,r=O`ddd`;for(let _ of r){let Q=v(e,t);if(!Q){let e=j(t);return u(a,o(r,e))}let i,h,Z=Q.p,q=Q.n;if(0==Q.k){i=P(Z)?O`^_a`:O`MNO`,h=.1+.38*m(1-A(t[1]))}else i=Q.s.c,h=Q.s.f;let x=v(u(Z,c(q,1e-4)),V)?.t<20?.18:1,y=(x?1:0)*U(0,b(q,g(R(V,t))))**(Q.k?120:70),G=u(c(i,x*(.1+.9*U(0,b(q,V)))*(.65+.35*q[1])),c(O`ddd`,y*(Q.k?.55:.35)+.18*U(0,1+b(t,q))**2));if(a=u(a,o(r,G)),h<.001)break;r=c(r,h),e=u(Z,c(q,1e-4)),t=g(d(t,q))}return a};S||=[O`UdPN^9U=`,O`SM]d\\QS.`,O`WbbdbbWD`,O`Pd\`NXHPM`];for(let l=0;l<H;l++){let a=.4*(1-2*(l+.5)/H);for(let f=0;f<W;f++){let n=z(C,g(u(u(c(y,.4*(2*(f+.5)/W-1)*(W/H)),c(G,a)),w))).map((e=>(e/(1+e))**(1/2.2)));n=(e=>n.map((t=>m(1.6875*t-.4375*e-.125))))(b(n,[.2126,.7152,.0722]));let p=(f+.5)/W-.5,i=(l+.5)/H-.5,k=m(1-.85*(p*p+i*i));n=c(n,k);let o=4*(l*W+f);D.set(c(n,255),o),D[o+3]=255}}return I}
```

**Parameters:**
- `W`, `H` — width/height in pixels (default: 256×256)
- `S` — scene array of spheres: `[[radius, r, g, b, reflectivity, x, y, z], ...]`
- `C` — camera position `[x, y, z]` (default: `[0, 1.4, 4]`)
- `L` — look-at target `[x, y, z]` (default: `[0, 0.8, -2]`)
- `P` — plane texture function `([x,y,z]) => 0|1` (default: checkerboard)

**Encoding spheres:** The default scene uses encoded strings. To create custom scenes, use arrays directly:

```javascript
// [radius, r, g, b, reflectivity, x, y, z]
const customScene = [
  [0.8, 1, 0.2, 0.2, 0.3, 0, 0.8, 0],    // red sphere
  [0.5, 0.2, 1, 0.2, 0.5, -1.5, 0.5, 1], // green sphere, more reflective
  [1.2, 1, 1, 1, 0.9, 2, 1.2, -1],       // large white mirror sphere
];
const img = makeTestImage(512, 512, customScene);
```

**Preset scenes:**

```javascript
const SCENES = {
  // Classic 4-sphere demo
  DEFAULT: [
    [0.6, 0.9, 0.2, 0.3, 0.3, -1.0, 0.6, 0],      // red-pink left
    [0.5, 0.2, 0.8, 0.9, 0.4, 0.8, 0.5, 0.5],     // cyan right-front
    [0.8, 0.95, 0.95, 1.0, 0.85, 0.3, 0.8, -0.8], // white mirror
    [0.4, 1.0, 0.9, 0.3, 0.2, -0.3, 0.4, 0.8],    // yellow front
  ],
  
  // Single large mirror sphere
  MIRROR: [[1.2, 0.98, 0.98, 1.0, 0.95, 0, 1.2, 0]],
  
  // RGB spheres in a row
  RGB: [
    [0.55, 1.0, 0.15, 0.15, 0.25, -1.1, 0.55, 0],
    [0.55, 0.15, 1.0, 0.15, 0.25, 0, 0.55, 0],
    [0.55, 0.15, 0.15, 1.0, 0.25, 1.1, 0.55, 0],
  ],
  
  // Metallic gold and silver
  METALLIC: [
    [0.7, 0.9, 0.8, 0.3, 0.7, -0.8, 0.7, 0],
    [0.7, 0.8, 0.8, 0.85, 0.8, 0.8, 0.7, 0],
  ],
};

// Custom plane textures
const PLANE_TEXTURES = {
  checker: ([x,,z]) => (8*x & 1) ^ (8*z & 1),
  stripes: ([x,,z]) => (4*z & 1),
  dots: ([x,,z]) => (Math.hypot(x % 1 - 0.5, z % 1 - 0.5) < 0.3) ? 1 : 0,
};
```

**Usage with output converters:**

```javascript
// Generate and display
const imageData = makeTestImage(512, 512);
const canvas = document.createElement('canvas');
canvas.width = imageData.width;
canvas.height = imageData.height;
canvas.getContext('2d').putImageData(imageData, 0, 0);
document.body.appendChild(canvas);

// As data URL
const dataUrl = canvas.toDataURL('image/png');

// As ImageBitmap
const bitmap = await createImageBitmap(imageData);
```

## Future: Additional Test Patterns

Placeholder for simpler test pattern generators:
- Checkerboard, gradient, color bars
- Resolution/sharpness test patterns  
- Placeholder images with dimensions overlay

## Arrow Path Generator

Generate arrow paths programmatically with correct head angles using `scripts/arrow-path.js`:

```bash
# Simple arrow from (0,0) to (100,50)
node scripts/arrow-path.js 0 0 100 50

# Origin-centered arrow pointing right, 48px long (for simpleImage)
node scripts/arrow-path.js --centered 1 0 48

# Open chevron (fill-safe, stroke-only)
node scripts/arrow-path.js --centered 1 0 48 --head-type open

# Tapered shaft
node scripts/arrow-path.js 0 0 80 40 --base-wid 12 --neck-wid 4 --head-wid 20

# Using a preset
node scripts/arrow-path.js --preset tapered 0 0 100 50

# Show encoded form
node scripts/arrow-path.js --centered 1 0 48 --encode
```

### CLI Argument Order

**Important:** The CLI expects coordinates as positional arguments. Options can come before or after, but coordinates must be contiguous:

```bash
# CORRECT - options before coordinates
node scripts/arrow-path.js --head-len 16 --head-wid 18 0 0 100 50

# CORRECT - options after coordinates  
node scripts/arrow-path.js 0 0 100 50 --head-len 16 --head-wid 18

# CORRECT - centered mode with options
node scripts/arrow-path.js --centered 1 0 48 --head-type open
```

### Using as a Module (Recommended for Complex Cases)

For diagonal arrows, custom modulators, or piping to other scripts, use as a module:

```javascript
const { arrowPathD, arrowPathCentered, PRESETS } = require('./scripts/arrow-path.js');
const { encodePath } = require('./scripts/path-codec.js');

// Diagonal arrow from point A to point B
const d = arrowPathD(-18, 12, 20, -10, { headLen: 16, headWid: 18 });

// Encode for compact storage
const encoded = encodePath(d);

// Origin-centered arrow (for simpleImage icons)
const d2 = arrowPathCentered(1, -1, 48, { headType: 'open' });
```

### Piping to save_png.js

Generate and render in one pipeline:

```bash
# Using node -e for complex arrow generation
node -e "
const { arrowPathD } = require('./scripts/arrow-path.js');
const { encodePath } = require('./scripts/path-codec.js');
const d = arrowPathD(-18, 12, 20, -10, { headLen: 16, headWid: 18 });
console.log(encodePath(d));
" | node scripts/save_png.js --stdin --encoded-path --size 96 --out arrow.png

# Simple case - raw path output
node scripts/arrow-path.js 0 0 48 0 | node scripts/save_png.js --stdin --out arrow.png
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

## Usage Examples

```javascript
// Paths are centered at origin. Arrow path: M-22 0 L22 0 M8 -14 L22 0 L8 14
const arrow = simpleImage("M-22 0 L22 0 M8 -14 L22 0 L8 14", 64, 64, {
  fill: "#0000", stroke: "#333", thickness: 4
});

// NAND gate symbol at 64×64 (default scale)
const nand = simpleImage(PATHS.NAND_GATE, 64, 64, {
  fill: "#fff", stroke: "#000", thickness: 2
});

// Same icon at 48×48 - just use scale parameter
const nandSmall = simpleImage(PATHS.NAND_GATE, 48, 48, {
  fill: "#fff", stroke: "#000", thickness: 1.5, scale: 48/64
});

// Convert to blob and use as img src
const blob = await arrow.convertToBlob({ type: "image/png" });
const img = new Image();
img.src = URL.createObjectURL(blob);

// Draw to visible canvas
const ctx = document.getElementById("myCanvas").getContext("2d");
ctx.drawImage(nand, 0, 0);
```

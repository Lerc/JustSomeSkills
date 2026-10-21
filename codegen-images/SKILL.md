---
name: codegen-images
description: Generates icons, schematic symbols and raytraced placeholder images in plain JavaScript, using a library of 72 origin-centered SVG paths (UI, electronics, shapes), a compact path encoding, and Node scripts that write PNG files. Use when a page or program needs icons, glyphs, circuit symbols, or placeholder/test images without fetching external image files, or when another task needs small PNG icons.
---

# Codegen Images

Draw images in code so a page needs no external image files. Resolve
`<skill-dir>` as the directory containing this `SKILL.md`; run scripts and read
references by their resolved paths.

| Need | Read |
|---|---|
| An icon or symbol in a page | This file, then [common-paths.md](references/common-paths.md) for ready-made paths |
| A new stroke-only path (outline, chevron, curve) | [fill-safe-paths.md](references/fill-safe-paths.md) |
| Arrows at arbitrary angles or tapered | [arrow-generator.md](references/arrow-generator.md) |
| Smallest possible embedded path data | [path-encoding.md](references/path-encoding.md) |
| A placeholder/test photo-like image | [test-images.md](references/test-images.md) |
| PNG files on disk | [PNG files](#png-files-nodejs) below |

`<skill-dir>/sampler.html` previews every library path at 16–128 px and the
raytraced scenes. Open it when you need to pick an icon visually.

## simpleImage: render a path to a canvas

Paste this into the page:

```javascript
function simpleImage(p="M-22 -22 h44 v44 h-44 Z",w=64,h=w,o={}){let{background:b="#0000",stroke:s="#000f",fill:f="#fffa",thickness:t=w/32,transform:m=[1,0,0,1,0,0],scale:c=1,angle:a=0}=o;const C=new OffscreenCanvas(w,h),X=C.getContext("2d");let P=new Path2D(p);m instanceof DOMMatrix||(m=new DOMMatrix(m));m.translateSelf(w/2,h/2);m.rotateSelf(a);m.scaleSelf(c,c);let T=new Path2D;T.addPath(P,m);P=T;X.fillStyle=b;X.fillRect(0,0,w,h);X.fillStyle=f;X.strokeStyle=s;X.lineWidth=t;X.stroke(P);X.fill(P);return C}
```

`simpleImage(path, width=64, height=width, opts)` returns an `OffscreenCanvas`.

| Option | Default | Meaning |
|---|---|---|
| `background` | `"#0000"` | Canvas background |
| `stroke`, `fill` | `"#000f"`, `"#fffa"` | Path colours; `fill: "#0000"` for outline-only rendering |
| `thickness` | `width/32` | Stroke width |
| `scale`, `angle` | `1`, `0` | Extra scale factor; rotation in degrees |
| `transform` | identity | Base matrix `[a,b,c,d,e,f]` or `DOMMatrix`, applied after centering |

**Path conventions.** Paths are centered on the origin with content spanning
about −24..+24, so at `scale: 1` they fill a 64×64 canvas with ~8 px padding.
For other sizes scale proportionally: `simpleImage(d, 32, 32, { scale: 32/64 })`.

**Every path is both stroked and filled.** A shape meant to be stroke-only must
enclose zero area, or it renders filled whenever `fill` is visible. The library
paths already follow this. Read [fill-safe-paths.md](references/fill-safe-paths.md)
before writing a new one.

```javascript
const PATHS = {
  CHECK: "M-22 2 L-6 18 m 0 0 L22 -18",
  NAND_GATE: "M-20 -16 L-4 -16 A16 16 0 0 1 -4 16 L-20 16 Z M12 0 A4 4 0 0 1 20 0 A4 4 0 0 1 12 0",
};
const check = simpleImage(PATHS.CHECK, 64, 64, { fill: "#0000", stroke: "#0a0", thickness: 4 });
const nand = simpleImage(PATHS.NAND_GATE, 48, 48, { fill: "#fff", stroke: "#000", thickness: 1.5, scale: 48/64 });
```

## Using the canvas

```javascript
ctx.drawImage(canvas, x, y);                                  // draw onto a visible canvas

const blob = await canvas.convertToBlob({ type: "image/png" });
img.src = URL.createObjectURL(blob);                          // blob: URL for <img>, CSS

const dataUrl = await new Promise(r => {                      // data: URL (serialisable)
  const fr = new FileReader(); fr.onload = () => r(fr.result); fr.readAsDataURL(blob);
});

const bitmap = await createImageBitmap(canvas);               // transferable to workers
const pixels = canvas.getContext("2d").getImageData(0, 0, canvas.width, canvas.height);
```

## PNG files (Node.js)

The scripts need `@napi-rs/canvas`. Node resolves it from the script's
location, not the current directory, so install it once and point `NODE_PATH`
at it:

```bash
npm install --prefix "${TMPDIR:-/tmp}/codegen-images-deps" @napi-rs/canvas
export NODE_PATH="${TMPDIR:-/tmp}/codegen-images-deps/node_modules"
```

```bash
node <skill-dir>/scripts/save_png.js --preset nand_gate --size 48 --fill "#fff" --stroke "#000" --out nand.png
node <skill-dir>/scripts/save_png.js --path "M-16 -20 L20 0 -16 20 Z" --size 64 --out icon.png
node <skill-dir>/scripts/save_png.js --list-presets      # every library path, lowercase name
node <skill-dir>/scripts/save_png.js --help              # stroke, fill, background, scale, rotation, stdin
```

`--scale` defaults to `size/64`, so library paths keep the same padding at any
size.

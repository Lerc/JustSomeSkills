#!/usr/bin/env node
/**
 * save_png.js - Generate PNG images from SVG path data
 * 
 * Paths should be centered at origin (0,0), spanning roughly -24 to +24.
 * 
 * Usage:
 *   node save_png.js --path "M-16 -20 L20 0 -16 20 Z" --out icon.png
 *   node save_png.js --encoded-path "!:N\$fN!RV#bN#RF3" --out icon.png
 *   node save_png.js --preset arrow_right --size 48 --out arrow.png
 *   echo "M0 -20 L20 0 0 20 Z" | node save_png.js --stdin --out icon.png
 *   node arrow-path.js --centered 1 0 48 | node save_png.js --stdin --out arrow.png
 * 
 * Options:
 *   --path <svg-path>         SVG path data string (origin-centered)
 *   --encoded-path <enc>      Encoded path string (will be decoded)
 *   --stdin                   Read path from stdin (use with --path or --encoded-path)
 *   --preset <name>           Use a preset path (see --list-presets)
 *   --size <n>                Width and height in pixels (default: 64)
 *   --width <n>               Width in pixels (overrides --size)
 *   --height <n>              Height in pixels (overrides --size)
 *   --fill <color>            Fill color (default: #fffa)
 *   --stroke <color>          Stroke color (default: #000f)
 *   --background <color>      Background color (default: transparent)
 *   --thickness <n>           Stroke width (default: size/32)
 *   --scale <n>               Scale factor (default: min(width, height)/64, so
 *                             library paths keep the same padding at any size)
 *   --angle <deg>             Rotation in degrees (default: 0)
 *   --out <file>              Output filename (required)
 *   --list-presets            Show available preset paths
 * 
 * Piping examples:
 *   # Generate arrow and save as PNG in one pipeline
 *   node arrow-path.js --centered 1 0 48 | node save_png.js --stdin --out arrow.png
 *   
 *   # Decode and render an encoded path
 *   echo "!:N\$fN!RV#bN#RF3" | node save_png.js --stdin --encoded-path --out icon.png
 * 
 * Requires @napi-rs/canvas (or canvas) resolvable from this script; see SKILL.md.
 */

// --help prints the usage comment above (before loading canvas, so it works without it)
if (require.main === module && process.argv.slice(2).some(a => a === '--help' || a === '-h')) {
  const src = require('fs').readFileSync(__filename, 'utf8');
  console.log(src.slice(src.indexOf('/**') + 3, src.indexOf('*/')).replace(/^ \* ?/gm, '').trim());
  process.exit(0);
}

// Use @napi-rs/canvas (prebuilt binaries) or fallback to 'canvas' package
let createCanvas, Path2D;
try {
  const napi = require('@napi-rs/canvas');
  createCanvas = napi.createCanvas;
  Path2D = napi.Path2D;
} catch {
  const canvas = require('canvas');
  createCanvas = canvas.createCanvas;
  Path2D = global.Path2D || canvas.Path2D;
}
const fs = require('fs');

// Path decoder (case-aware: uppercase=0.1 precision, lowercase=0.01 precision)
function decodePath(e) {
  let c, t, n, d = "", l = 0, o = c => e.charCodeAt(l++) - 33;
  for (; l < e.length; d += t < 20 ? (c = 1 & t ? 100 : 10, "MmLlHhVvCcSsQqTtAaZz"[t]) : t < 71 ? t - 45 + " " : 71 == t ? (n = o(), e.slice(l, l += n)) : (94 * (t - 72) + o() - 1033) / c + " ") t = o();
  return d;
}

// Preset paths: every path in references/common-paths.md, by lowercase name (e.g. nand_gate)
const PRESETS = Object.fromEntries(
  Object.values(require('./path-codec.js').loadPathLibrary())
    .flatMap(paths => Object.entries(paths))
    .map(([name, d]) => [name.toLowerCase(), d])
);

function parseArgs(args) {
  const opts = {
    path: null,
    encodedPath: null,
    useEncodedPath: false,  // flag for stdin mode
    stdin: false,
    preset: null,
    size: 64,
    width: null,
    height: null,
    fill: '#fffa',
    stroke: '#000f',
    background: '#0000',
    thickness: null,
    scale: null,
    angle: 0,
    out: null,
    listPresets: false,
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    const next = args[i + 1];

    switch (arg) {
      case '--path': opts.path = next; i++; break;
      case '--encoded-path':
        // Check if next arg exists and doesn't start with --
        if (next && !next.startsWith('--')) {
          opts.encodedPath = next;
          i++;
        } else {
          // Flag-only mode for use with --stdin
          opts.useEncodedPath = true;
        }
        break;
      case '--stdin': opts.stdin = true; break;
      case '--preset': opts.preset = next; i++; break;
      case '--size': opts.size = parseInt(next, 10); i++; break;
      case '--width': opts.width = parseInt(next, 10); i++; break;
      case '--height': opts.height = parseInt(next, 10); i++; break;
      case '--fill': opts.fill = next; i++; break;
      case '--stroke': opts.stroke = next; i++; break;
      case '--background': opts.background = next; i++; break;
      case '--thickness': opts.thickness = parseFloat(next); i++; break;
      case '--scale': opts.scale = parseFloat(next); i++; break;
      case '--angle': opts.angle = parseFloat(next); i++; break;
      case '--out': opts.out = next; i++; break;
      case '--list-presets': opts.listPresets = true; break;
    }
  }

  return opts;
}

function simpleImage(pathData, width, height, opts = {}) {
  const {
    background = '#0000',
    stroke = '#000f',
    fill = '#fffa',
    thickness = width / 32,
    lineCap = 'round',
    lineJoin = 'round',
    scale = 1,
    angle = 0
  } = opts;

  const canvas = createCanvas(width, height);
  const ctx = canvas.getContext('2d');

  // Draw background
  ctx.fillStyle = background;
  ctx.fillRect(0, 0, width, height);

  // For origin-centered paths: translate to center, rotate, scale
  ctx.translate(width / 2, height / 2);
  ctx.rotate((angle * Math.PI) / 180);
  ctx.scale(scale, scale);

  // Draw path
  const path2d = new Path2D(pathData);
  ctx.fillStyle = fill;
  ctx.strokeStyle = stroke;
  ctx.lineWidth = thickness / scale; // Adjust thickness for scale
  ctx.lineCap = lineCap;
  ctx.lineJoin = lineJoin;
  ctx.fill(path2d);
  ctx.stroke(path2d);

  return canvas;
}

function readStdin() {
  return new Promise((resolve, reject) => {
    let data = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('readable', () => {
      let chunk;
      while ((chunk = process.stdin.read()) !== null) {
        data += chunk;
      }
    });
    process.stdin.on('end', () => resolve(data.trim()));
    process.stdin.on('error', reject);
    
    // Handle case where stdin is a TTY (no piped input)
    if (process.stdin.isTTY) {
      resolve('');
    }
  });
}

async function main() {
  const args = process.argv.slice(2);
  const opts = parseArgs(args);

  if (opts.listPresets) {
    console.log('Available presets:\n');
    for (const [name, pathData] of Object.entries(PRESETS)) {
      console.log(`  ${name.padEnd(15)} ${pathData.slice(0, 50)}${pathData.length > 50 ? '...' : ''}`);
    }
    process.exit(0);
  }

  // Handle stdin input
  if (opts.stdin) {
    const stdinData = await readStdin();
    if (!stdinData) {
      console.error('Error: No data received from stdin');
      process.exit(1);
    }
    
    // Determine if stdin should be treated as encoded or raw path
    if (opts.useEncodedPath || opts.encodedPath !== null) {
      // --encoded-path flag present means decode stdin
      opts.encodedPath = stdinData;
    } else {
      // Default: treat stdin as raw path
      opts.path = stdinData;
    }
  }

  // Resolve path
  let pathData = opts.path;
  
  if (opts.encodedPath) {
    // Decode the encoded path
    pathData = decodePath(opts.encodedPath);
  } else if (opts.preset) {
    pathData = PRESETS[opts.preset];
    if (!pathData) {
      console.error(`Unknown preset: ${opts.preset}`);
      console.error('Use --list-presets to see available presets');
      process.exit(1);
    }
  }

  if (!pathData) {
    console.error('Error: Must specify --path, --encoded-path, --preset, or use --stdin');
    process.exit(1);
  }

  if (!opts.out) {
    console.error('Error: Must specify --out <filename>');
    process.exit(1);
  }

  const width = opts.width || opts.size;
  const height = opts.height || opts.size;
  const thickness = opts.thickness || width / 32;

  const canvas = simpleImage(pathData, width, height, {
    fill: opts.fill,
    stroke: opts.stroke,
    background: opts.background,
    thickness,
    scale: opts.scale ?? Math.min(width, height) / 64,
    angle: opts.angle,
  });

  // Save to file
  const buffer = canvas.toBuffer('image/png');
  fs.writeFileSync(opts.out, buffer);
  console.log(`Saved: ${opts.out} (${width}x${height})`);
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});

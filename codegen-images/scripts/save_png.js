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
 *   --scale <n>               Scale factor (default: 1)
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
 * Requires: npm install @napi-rs/canvas (or canvas)
 */

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

// Preset paths library (origin-centered, content spans -24 to +24)
const PRESETS = {
  // UI
  arrow_right: "M-16 -20 L20 0 -16 20 Z",
  arrow_left: "M16 -20 L-20 0 16 20 Z",
  arrow_up: "M-20 16 L0 -20 20 16 Z",
  arrow_down: "M-20 -16 L0 20 20 -16 Z",
  chevron_right: "M-12 -20 L12 0 -12 20",
  chevron_left: "M12 -20 L-12 0 12 20",
  close: "M-20 -20 L20 20 M20 -20 L-20 20",
  check: "M-22 2 L-6 18 22 -18",
  plus: "M0 -22 L0 22 M-22 0 L22 0",
  minus: "M-22 0 L22 0",
  hamburger: "M-22 -16 L22 -16 M-22 0 L22 0 M-22 16 L22 16",
  play: "M-16 -22 L20 0 -16 22 Z",
  pause: "M-18 -22 L-6 -22 -6 22 -18 22 Z M6 -22 L18 -22 18 22 6 22 Z",
  stop: "M-20 -20 L20 -20 20 20 -20 20 Z",
  star: "M0 -24 L6 -6 24 -6 10 6 16 24 0 14 -16 24 -10 6 -24 -6 -6 -6 Z",
  heart: "M0 20 L-20 0 A12 12 0 0 1 0 -14 12 12 0 0 1 20 0 Z",
  gear: "M-2 -24 L2 -24 4 -18 10 -16 16 -20 19 -17 15 -10 17 -4 24 -2 24 2 18 4 16 10 20 16 17 19 10 15 4 17 2 24 -2 24 -4 18 -10 16 -16 20 -19 17 -15 10 -17 4 -24 2 -24 -2 -18 -4 -16 -10 -20 -16 -17 -19 -10 -15 -4 -17 Z M0 -8 A8 8 0 1 0 0 8 8 8 0 1 0 0 -8",
  
  // Electronics (updated to match common-paths.md)
  and_gate: "M-20 -16 L-4 -16 A16 16 0 0 1 -4 16 L-20 16 Z M20 0 L12 0",
  or_gate: "M-20 -16 Q-8 -16 12 0 Q-8 16 -20 16 Q-8 0 -20 -16 M12 0 L20 0",
  not_gate: "M-20 -16 L-20 16 L8 0 Z M8 0 A4 4 0 0 1 16 0 A4 4 0 0 1 8 0 M16 0 L20 0",
  nand_gate: "M-20 -16 L-4 -16 A16 16 0 0 1 -4 16 L-20 16 Z M12 0 A4 4 0 0 1 20 0 A4 4 0 0 1 12 0",
  resistor: "M0 -24 L0 -16 -8 -12 8 -4 -8 4 8 12 0 16 0 24",
  capacitor: "M0 -24 L0 -8 M-16 -8 L16 -8 M-16 8 L16 8 M0 8 L0 24",
  diode: "M24 0 L12 0 M12 -12 L12 12 M12 0 L-12 -12 L-12 12 Z M-12 0 L-24 0",
  gnd: "M0 -24 L0 -4 M-16 -4 L16 -4 M-10 4 L10 4 M-4 12 L4 12",
  
  // Shapes
  triangle: "M0 -24 L24 18 -24 18 Z",
  square: "M-22 -22 L22 -22 22 22 -22 22 Z",
  diamond: "M0 -24 L24 0 0 24 -24 0 Z",
  hexagon: "M-13 -20 L-24 0 L-13 20 H13 L24 0 L13 -20 Z",
  circle: "M0 -24 C14 -24 24 -14 24 0 24 14 14 24 0 24 -14 24 -24 14 -24 0 -24 -14 -14 -24 0 -24 Z",
  
  // Misc
  hook: "M-8 -24 L-8 4 Q-8 20 8 20 20 20 20 8 L20 4",
  warning: "M0 -24 L24 20 -24 20 Z M0 -8 L0 6 M0 12 L0 14",
  cursor: "M-20 -24 L-20 16 -8 8 0 24 8 20 0 4 16 4 Z",
};

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
    scale: 1,
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
    scale: opts.scale,
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

#!/usr/bin/env node
/**
 * Arrow path generator - creates SVG path `d` strings for arrows
 * 
 * Usage as module:
 *   const { arrowPathD } = require('./arrow-path.js');
 *   const d = arrowPathD(0, 0, 100, 50, { headType: 'filled', headLen: 14 });
 * 
 * Usage as CLI:
 *   node arrow-path.js 0 0 100 50
 *   node arrow-path.js 0 0 100 50 --head-type open --head-len 20
 *   node arrow-path.js --help
 * 
 * Features:
 *   - Filled or open (stroke-only, fill-safe) head types
 *   - Tapered or untapered shafts
 *   - Modulator functions for curved/wavy arrows
 *   - Encoder-aware quantization (0.1 abs, 0.01 rel) for compact encoding
 */

/* -------------------- helpers: formatting + offsetting -------------------- */

function fmt(n) {
  if (Math.abs(n) < 1e-12) n = 0;
  const s = n.toFixed(3);
  return s.replace(/\.000$/, '').replace(/(\.\d*?)0+$/, '$1').replace(/\.$/, '');
}

function fmtLit(n) {
  if (Math.abs(n) < 1e-12) n = 0;
  let s = n.toFixed(6);
  while (s.includes('.') && s.endsWith('0')) s = s.slice(0, -1);
  if (s.endsWith('.')) s = s.slice(0, -1);
  return s;
}

/**
 * Offset ONLY absolute 'M' and 'L' coordinates.
 * Generator emits only: M, L, m, l, Z/z.
 */
function offsetML(d, ox, oy) {
  if (!d) return d;

  const isCmd = c => /[a-zA-Z]/.test(c);
  const isNumStart = c => c === '+' || c === '-' || c === '.' || (c >= '0' && c <= '9');

  const tokens = [];
  let i = 0;

  while (i < d.length) {
    const c = d[i];

    if (isCmd(c)) { tokens.push({ t: 'cmd', v: c }); i++; continue; }

    if (isNumStart(c)) {
      let j = i + 1;
      while (j < d.length) {
        const cj = d[j];
        if (cj === 'e' || cj === 'E') {
          j++;
          if (d[j] === '+' || d[j] === '-') j++;
          continue;
        }
        if (isNumStart(cj) || (cj >= '0' && cj <= '9')) { j++; continue; }
        break;
      }
      tokens.push({ t: 'num', v: d.slice(i, j) });
      i = j;
      continue;
    }

    let j = i + 1;
    while (j < d.length && !isCmd(d[j]) && !isNumStart(d[j])) j++;
    tokens.push({ t: 'sep', v: d.slice(i, j) });
    i = j;
  }

  let out = '';
  let cmd = '';
  let pair = 0;
  for (const tok of tokens) {
    if (tok.t === 'cmd') { cmd = tok.v; pair = 0; out += tok.v; continue; }
    if (tok.t !== 'num') { out += tok.v; continue; }

    if (cmd === 'M' || cmd === 'L') {
      const n = Number(tok.v);
      const v = pair === 0 ? (n + ox) : (n + oy);
      out += fmtLit(v);
      pair ^= 1;
    } else {
      out += tok.v;
    }
  }
  return out;
}

/* -------------------- core generator -------------------- */

function arrowDenc(dx, dy, {
  headLen = 14,
  baseWid = 0,
  neckWid = baseWid / 3,
  headWid = neckWid + 10,
  shorten = true,
  segments = 1,
  modulator = a => 0,
  minLen = 2,
  headType = 'filled'
} = {}) {
  const L = Math.hypot(dx, dy);
  if (!(L > 0)) return '';

  const ux = dx / L, uy = dy / L;
  const px = -uy, py = ux;

  const ABS_S = 10;
  const REL_S = 100;
  const RAW_MIN = -1033;
  const RAW_MAX = 1034;

  function qEnc(v, s) {
    const ri = Math.round(v);
    if (Math.abs(ri) <= 25 && Math.abs(v - ri) < 1e-9) return { v: ri, esc: false };

    const minV = RAW_MIN / s;
    const maxV = RAW_MAX / s;
    if (v >= minV && v <= maxV) return { v: Math.round(v * s) / s, esc: false };

    return { v, esc: true };
  }

  function fmtEnc(o) { return o && o.esc ? fmtLit(o.v) : fmt(o.v); }

  segments = Math.max(1, segments | 0);

  const hl = Math.min(headLen, L);
  const tapered = (baseWid !== 0) || (neckWid !== 0);

  const shaftLen = (shorten && L > hl + minLen) ? (L - hl) : L;

  function centerAt(t) {
    const s = shaftLen * t;
    const off = (modulator(t) || 0) * L;
    return { x: ux * s + px * off, y: uy * s + py * off };
  }

  const tx = dx, ty = dy;

  // ---------------- Untapered (centerline) ----------------
  if (!tapered) {
    const pts = [];
    for (let i = 0; i <= segments; i++) pts.push(centerAt(i / segments));

    const hw = headWid * 0.5;
    const hx = tx - ux * hl;
    const hy = ty - uy * hl;
    const lx = hx + px * hw, ly = hy + py * hw;
    const rx = hx - px * hw, ry = hy - py * hw;

    const breaker = headType === 'open' ? 'm 0 0 ' : '';
    if (headType === 'open') pts[pts.length - 1] = { x: tx, y: ty };

    let d = '';
    d += `M ${fmtEnc(qEnc(pts[0].x, ABS_S))} ${fmtEnc(qEnc(pts[0].y, ABS_S))} `;

    for (let i = 1; i < pts.length; i++) {
      const dxr = pts[i].x - pts[i - 1].x;
      const dyr = pts[i].y - pts[i - 1].y;
      d += `l ${fmtEnc(qEnc(dxr, REL_S))} ${fmtEnc(qEnc(dyr, REL_S))} ${breaker}`;
    }

    if (headType === 'open') {
      const tlx = qEnc(lx - tx, REL_S), tly = qEnc(ly - ty, REL_S);
      const ltx = qEnc(tx - lx, REL_S), lty = qEnc(ty - ly, REL_S);
      const trx = qEnc(rx - tx, REL_S), try_ = qEnc(ry - ty, REL_S);
      const rtx = qEnc(tx - rx, REL_S), rty = qEnc(ty - ry, REL_S);

      d += `m ${fmtEnc(tlx)} ${fmtEnc(tly)} l ${fmtEnc(ltx)} ${fmtEnc(lty)} m 0 0 `;
      d += `m ${fmtEnc(trx)} ${fmtEnc(try_)} l ${fmtEnc(rtx)} ${fmtEnc(rty)}`;
      return d.trim();
    }

    d += `M ${fmtEnc(qEnc(lx, ABS_S))} ${fmtEnc(qEnc(ly, ABS_S))} `;
    d += `L ${fmtEnc(qEnc(tx, ABS_S))} ${fmtEnc(qEnc(ty, ABS_S))} `;
    d += `L ${fmtEnc(qEnc(rx, ABS_S))} ${fmtEnc(qEnc(ry, ABS_S))} Z`;
    return d.trim();
  }

  // ---------------- Tapered (outline) ----------------
  const ptsL = [];
  const ptsR = [];

  for (let i = 0; i <= segments; i++) {
    const t = i / segments;
    const s = shaftLen * t;
    const off = (modulator(t) || 0) * L;

    const cx0 = ux * s;
    const cy0 = uy * s;

    const w = baseWid + (neckWid - baseWid) * t;
    const hw = w * 0.5;

    ptsL.push({ x: cx0 + px * (hw + off), y: cy0 + py * (hw + off) });
    ptsR.push({ x: cx0 + px * (-hw - off), y: cy0 + py * (-hw - off) });
  }

  const offEnd = (modulator(1) || 0) * L;
  const cxEnd0 = ux * shaftLen;
  const cyEnd0 = uy * shaftLen;

  const headHW = headWid * 0.5;
  const hL = { x: cxEnd0 + px * (headHW + offEnd), y: cyEnd0 + py * (headHW + offEnd) };
  const hR = { x: cxEnd0 + px * (-headHW - offEnd), y: cyEnd0 + py * (-headHW - offEnd) };

  const breaker = headType === 'open' ? 'm 0 0 ' : '';

  let d = '';
  d += `M ${fmtEnc(qEnc(ptsL[0].x, ABS_S))} ${fmtEnc(qEnc(ptsL[0].y, ABS_S))} `;

  for (let i = 1; i < ptsL.length; i++) {
    const dxr = ptsL[i].x - ptsL[i - 1].x;
    const dyr = ptsL[i].y - ptsL[i - 1].y;
    d += `l ${fmtEnc(qEnc(dxr, REL_S))} ${fmtEnc(qEnc(dyr, REL_S))} ${breaker}`;
  }

  {
    const lastL = ptsL[ptsL.length - 1];
    const dxr = hL.x - lastL.x;
    const dyr = hL.y - lastL.y;
    d += `l ${fmtEnc(qEnc(dxr, REL_S))} ${fmtEnc(qEnc(dyr, REL_S))} ${breaker}`;
  }

  {
    const dxr = tx - hL.x;
    const dyr = ty - hL.y;
    d += `l ${fmtEnc(qEnc(dxr, REL_S))} ${fmtEnc(qEnc(dyr, REL_S))} ${breaker}`;
  }

  {
    const dxr = hR.x - tx;
    const dyr = hR.y - ty;
    d += `l ${fmtEnc(qEnc(dxr, REL_S))} ${fmtEnc(qEnc(dyr, REL_S))} ${breaker}`;
  }

  {
    const lastR = ptsR[ptsR.length - 1];
    const dxr = lastR.x - hR.x;
    const dyr = lastR.y - hR.y;
    d += `l ${fmtEnc(qEnc(dxr, REL_S))} ${fmtEnc(qEnc(dyr, REL_S))} ${breaker}`;
  }

  for (let i = ptsR.length - 2; i >= 0; i--) {
    const curr = ptsR[i + 1];
    const next = ptsR[i];
    const dxr = next.x - curr.x;
    const dyr = next.y - curr.y;
    d += `l ${fmtEnc(qEnc(dxr, REL_S))} ${fmtEnc(qEnc(dyr, REL_S))} ${breaker}`;
  }

  if (headType === 'filled') d += 'z';
  return d.trim();
}

/* -------------------- main export -------------------- */

/**
 * Generate an arrow path from (startX, startY) to (tipX, tipY)
 * 
 * @param {number} startX - Start X coordinate
 * @param {number} startY - Start Y coordinate  
 * @param {number} tipX - Tip (end) X coordinate
 * @param {number} tipY - Tip (end) Y coordinate
 * @param {Object} opts - Options
 * @param {string} opts.headType - 'filled' or 'open' (fill-safe)
 * @param {number} opts.headLen - Head length along arrow direction (default: 14)
 * @param {number} opts.headWid - Head width at base (default: neckWid + 10)
 * @param {number} opts.baseWid - Shaft width at start (0 = centerline only)
 * @param {number} opts.neckWid - Shaft width at head (default: baseWid/3)
 * @param {boolean} opts.shorten - End shaft at head base (default: true)
 * @param {number} opts.segments - Shaft segments (default: 1)
 * @param {Function} opts.modulator - t => offset as fraction of length
 * @param {number} opts.minLen - Minimum length before head-only (default: 2)
 * @returns {string} SVG path d attribute
 */
function arrowPathD(startX, startY, tipX, tipY, opts = {}) {
  const dx = tipX - startX;
  const dy = tipY - startY;
  const d0 = arrowDenc(dx, dy, opts);
  return offsetML(d0, startX, startY);
}

/**
 * Generate an origin-centered arrow path (for use with simpleImage)
 * Arrow points in direction of (dx, dy), centered at origin
 * 
 * @param {number} dx - X component of direction
 * @param {number} dy - Y component of direction
 * @param {number} length - Total arrow length
 * @param {Object} opts - Same options as arrowPathD
 * @returns {string} SVG path d attribute, centered at origin
 */
function arrowPathCentered(dx, dy, length, opts = {}) {
  const mag = Math.hypot(dx, dy) || 1;
  const ux = dx / mag, uy = dy / mag;
  const halfLen = length / 2;
  return arrowPathD(-ux * halfLen, -uy * halfLen, ux * halfLen, uy * halfLen, opts);
}

// Preset configurations
const PRESETS = {
  // Simple triangle head, no shaft
  simple: { headType: 'filled', baseWid: 0, neckWid: 0, headLen: 14, headWid: 14 },
  
  // Open chevron head (fill-safe)
  chevron: { headType: 'open', baseWid: 0, neckWid: 0, headLen: 14, headWid: 14 },
  
  // Tapered shaft with filled head
  tapered: { headType: 'filled', baseWid: 12, neckWid: 4, headWid: 16, headLen: 14, segments: 4 },
  
  // Block arrow (constant width shaft)
  block: { headType: 'filled', baseWid: 8, neckWid: 8, headWid: 16, headLen: 12, segments: 1 },
  
  // Thin pointer
  pointer: { headType: 'filled', baseWid: 0, neckWid: 0, headLen: 20, headWid: 10 },
  
  // Wide head
  wide: { headType: 'filled', baseWid: 0, neckWid: 0, headLen: 12, headWid: 24 },
};

module.exports = { arrowPathD, arrowPathCentered, arrowDenc, PRESETS };

/* -------------------- CLI -------------------- */

if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.includes('--help') || args.includes('-h') || args.length === 0) {
    console.log(`Arrow Path Generator - creates SVG path d strings for arrows

USAGE:
  node arrow-path.js <startX> <startY> <tipX> <tipY> [options]
  node arrow-path.js --centered <dx> <dy> <length> [options]
  node arrow-path.js --preset <name> <startX> <startY> <tipX> <tipY>
  node arrow-path.js --list-presets

COORDINATES:
  startX startY    Arrow start point
  tipX tipY        Arrow tip (end) point

OPTIONS:
  --head-type <filled|open>   Head style (default: filled)
                              'open' is fill-safe for batch renderers
  --head-len <n>              Head length in pixels (default: 14)
  --head-wid <n>              Head width at base (default: neckWid + 10)
  --base-wid <n>              Shaft width at start, 0=centerline (default: 0)
  --neck-wid <n>              Shaft width at head (default: baseWid/3)
  --segments <n>              Shaft segments for curves (default: 1)
  --no-shorten                Don't shorten shaft at head base
  --preset <name>             Use a preset configuration
  --centered                  Generate origin-centered path (for simpleImage)
  --encode                    Also show encoded form using path-codec

PRESETS: ${Object.keys(PRESETS).join(', ')}

EXAMPLES:
  # Simple filled arrow from (0,0) to (100,50)
  node arrow-path.js 0 0 100 50

  # Open chevron arrow
  node arrow-path.js 0 0 100 0 --head-type open

  # Tapered arrow with wider head
  node arrow-path.js 0 0 80 40 --base-wid 12 --neck-wid 4 --head-wid 20

  # Origin-centered arrow pointing right, 48px long
  node arrow-path.js --centered 1 0 48

  # Using a preset
  node arrow-path.js --preset tapered 0 0 100 50

OUTPUT:
  The path uses encoder-aware quantization:
  - Absolute coords (M, L): 0.1 precision, ±103 range  
  - Relative coords (m, l): 0.01 precision, ±10.3 range
  - Small integers -25..25: single character when encoded`);
    process.exit(0);
  }

  if (args[0] === '--list-presets') {
    console.log('Available presets:\n');
    for (const [name, opts] of Object.entries(PRESETS)) {
      console.log(`  ${name.padEnd(10)} ${JSON.stringify(opts)}`);
    }
    process.exit(0);
  }

  // Parse options
  const opts = {};
  let coords = [];
  let centered = false;
  let presetName = null;
  let showEncoded = false;

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    const next = args[i + 1];

    if (arg === '--head-type') { opts.headType = next; i++; }
    else if (arg === '--head-len') { opts.headLen = parseFloat(next); i++; }
    else if (arg === '--head-wid') { opts.headWid = parseFloat(next); i++; }
    else if (arg === '--base-wid') { opts.baseWid = parseFloat(next); i++; }
    else if (arg === '--neck-wid') { opts.neckWid = parseFloat(next); i++; }
    else if (arg === '--segments') { opts.segments = parseInt(next); i++; }
    else if (arg === '--no-shorten') { opts.shorten = false; }
    else if (arg === '--preset') { presetName = next; i++; }
    else if (arg === '--centered') { centered = true; }
    else if (arg === '--encode') { showEncoded = true; }
    else if (!arg.startsWith('-')) { coords.push(parseFloat(arg)); }
  }

  // Apply preset
  if (presetName) {
    if (!PRESETS[presetName]) {
      console.error(`Unknown preset: ${presetName}`);
      console.error(`Available: ${Object.keys(PRESETS).join(', ')}`);
      process.exit(1);
    }
    Object.assign(opts, PRESETS[presetName]);
  }

  let d;
  if (centered) {
    if (coords.length < 3) {
      console.error('Centered mode requires: <dx> <dy> <length>');
      process.exit(1);
    }
    d = arrowPathCentered(coords[0], coords[1], coords[2], opts);
  } else {
    if (coords.length < 4) {
      console.error('Requires: <startX> <startY> <tipX> <tipY>');
      process.exit(1);
    }
    d = arrowPathD(coords[0], coords[1], coords[2], coords[3], opts);
  }

  console.log(d);

  if (showEncoded) {
    try {
      const { encodePath } = require('./path-codec.js');
      const enc = encodePath(d);
      console.log(`\nEncoded (${enc.length} chars): ${enc}`);
    } catch (e) {
      console.log('\n(path-codec.js not found for encoding)');
    }
  }
}

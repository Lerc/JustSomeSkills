#!/usr/bin/env node
/**
 * SVG Path Encoder/Decoder for compact storage
 * 
 * Codec spec (uses full contiguous ASCII range 33..126 = 94 symbols):
 * - v = charCode - 33
 * - Commands (20 codes): v = 0..19 => "MmLlHhVvCcSsQqTtAaZz"
 * - Small ints (51 codes): v = 20..70 => -25..25 (n = v-45)
 * - Escape literal: v = 71 => next char is length L (0..93), then copy next L chars
 * - 2-char fixed-point: v = 72..93 (22 values)
 *     hi = v-72 (0..21), lo = next index (0..93)
 *     raw = hi*94 + lo - 1033 (approx -1033..+1034)
 *     value = raw / div, where div depends on last command case:
 *       - uppercase (even cmd index) => div=10 (0.1 steps, range ~±103)
 *       - lowercase (odd cmd index)  => div=100 (0.01 steps, range ~±10.3)
 */

const B = 94, CH0 = 33;
const encChar = v => String.fromCharCode(CH0 + v);
const CMD = "MmLlHhVvCcSsQqTtAaZz";
const ESC = 71;
const SMALL0 = 20, SMALL_MIN = -25, SMALL_MAX = 25;
const FP_HI0 = 72, FP_OFF = 1033;

function encSmallInt(n) {
  return encChar(SMALL0 + (n - SMALL_MIN));
}

function encFixedPointExact(x, div) {
  if (!Number.isFinite(x)) return null;
  const xd = x * div;
  const r = Math.round(xd);
  const eps = 1e-10 * Math.max(1, Math.abs(xd));
  if (Math.abs(xd - r) > eps) return null; // must align to 1/div
  const u = r + FP_OFF;
  if (u < 0 || u >= 22 * B) return null; // hi must be 0..21
  const hi = (u / B) | 0;
  const lo = u - hi * B;
  return encChar(FP_HI0 + hi) + encChar(lo);
}

function encLiteral(str) {
  let out = "";
  for (let i = 0; i < str.length; i += 93) {
    const chunk = str.slice(i, i + 93);
    out += encChar(ESC) + encChar(chunk.length) + chunk;
  }
  return out;
}

const TOK_RE = /[A-Za-z]|[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?|[^A-Za-z0-9.+-]+/g;

function encodePath(d) {
  let out = "", cmdIndex = 0; // default to 'M' (even => div=10)
  const parts = d.match(TOK_RE) || [];
  
  for (const t of parts) {
    if (t.length === 1) {
      const ci = CMD.indexOf(t);
      if (ci >= 0) { out += encChar(ci); cmdIndex = ci; continue; }
    }
    if (/^[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?$/.test(t)) {
      let x = Number(t);
      if (Number.isFinite(x)) {
        if (Object.is(x, -0)) x = 0;
        if (Number.isInteger(x) && x >= SMALL_MIN && x <= SMALL_MAX) {
          out += encSmallInt(x);
          continue;
        }
        // div depends on last command parity: even=10, odd=100
        const div = (cmdIndex & 1) ? 100 : 10;
        const fp = encFixedPointExact(x, div);
        if (fp) { out += fp; continue; }
      }
      out += encLiteral(t + " ");
      continue;
    }
    if (!/^\s+$/.test(t)) out += encLiteral(t);
  }
  return out;
}

function decodePath(e) {
  let s, c, l, t = "", d = 0, n = _ => e.charCodeAt(d++) - 33;
  for (; d < e.length;
    t += c < 20 ? (s = c & 1 ? 100 : 10, CMD[c]) :
         c < 71 ? c - 45 + " " :
         71 == c ? (l = n(), e.slice(d, d += l)) :
                   (94 * (c - 72) + n() - 1033) / s + " "
  ) c = n();
  return t;
}

// Minified decoder as tagged template literal (197 bytes)
const DECODER_MINIFIED = `function Q([e]){let c,t,n,d="",l=0,o=c=>e.charCodeAt(l++)-33;for(;l<e.length;d+=t<20?(c=1&t?100:10,"MmLlHhVvCcSsQqTtAaZz"[t]):t<71?t-45+" ":71==t?(n=o(),e.slice(l,l+=n)):(94*(t-72)+o()-1033)/c+" ")t=o();return d}`;

// Export for use as module
module.exports = { encodePath, decodePath, DECODER_MINIFIED };

// CLI usage
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args[0] === '--decode' && args[1]) {
    console.log(decodePath(args[1]));
  } else if (args[0] === '--encode' && args[1]) {
    const enc = encodePath(args[1]);
    console.log(`Encoded: ${enc}`);
    console.log(`Original length: ${args[1].length}, Encoded length: ${enc.length}`);
    console.log(`Ratio: ${(enc.length / args[1].length).toFixed(3)}`);
    console.log(`Decoded: ${decodePath(enc)}`);
  } else if (args[0] === '--encode-all') {
    // Read paths from common-paths.md and output encoded JavaScript
    const fs = require('fs');
    const content = fs.readFileSync('./references/common-paths.md', 'utf8');
    
    // Parse sections and paths - look for actual section names
    const sections = {};
    let currentSection = null;
    const sectionRe = /^const (UI|ELECTRONICS|SHAPES|MISC) = \{/;
    const pathRe = /^\s*(\w+):\s*"([^"]+)"/;
    
    for (const line of content.split('\n')) {
      const secMatch = line.match(sectionRe);
      if (secMatch) {
        currentSection = secMatch[1];
        sections[currentSection] = {};
        continue;
      }
      // End section on closing brace
      if (currentSection && line.match(/^\};?\s*$/)) {
        currentSection = null;
        continue;
      }
      if (currentSection) {
        const pathMatch = line.match(pathRe);
        if (pathMatch) {
          const [, name, path] = pathMatch;
          const enc = encodePath(path);
          sections[currentSection][name] = enc;
          
          // Verify round-trip
          const dec = decodePath(enc);
          const origNorm = path.replace(/\s+/g, '');
          const decNorm = dec.replace(/\s+/g, '');
          if (origNorm !== decNorm) {
            console.error(`// WARNING: ${name} decode mismatch`);
          }
        }
      }
    }
    
    // Output JavaScript
    console.log('// Path decoder (197 bytes) - case-aware: uppercase=0.1 precision, lowercase=0.01 precision');
    console.log(DECODER_MINIFIED);
    console.log('');
    console.log('// Encoded paths - generated from common-paths.md');
    console.log('// To regenerate: node scripts/path-codec.js --encode-all');
    console.log('const PATHS = {');
    
    for (const [section, paths] of Object.entries(sections)) {
      console.log(`  ${section}: {`);
      const entries = Object.entries(paths);
      for (let i = 0; i < entries.length; i++) {
        const [name, enc] = entries[i];
        // Escape backticks and backslashes for template literal
        const escaped = enc.replace(/\\/g, '\\\\').replace(/`/g, '\\`');
        const comma = i < entries.length - 1 ? ',' : '';
        console.log(`    ${name}: Q\`${escaped}\`${comma}`);
      }
      console.log('  },');
    }
    console.log('};');
    
  } else if (args[0] === '--decoder') {
    console.log(DECODER_MINIFIED);
  } else {
    console.log(`SVG Path Encoder/Decoder for compact storage (case-aware precision)

USAGE:
  node path-codec.js --encode "M-16 -20 L20 0 Z"   Encode a single path
  node path-codec.js --decode "<encoded>"          Decode a single path  
  node path-codec.js --encode-all                  Encode all paths from common-paths.md
                                                   (outputs ready-to-use JavaScript)
  node path-codec.js --decoder                     Print minified decoder function

ENCODING SPEC (ASCII 33-126, 94 printable symbols):
  Commands (0-19):     M m L l H h V v C c S s Q q T t A a Z z
  Small ints (20-70):  -25 to +25 as single char
  Escape (71):         Next char = length, then literal string
  2-char numbers (72-93): Case-aware precision
    - After uppercase cmd: ÷10  → range ±103.3, step 0.1
    - After lowercase cmd: ÷100 → range ±10.33, step 0.01

WORKFLOW:
  1. Edit paths in references/common-paths.md (human-readable source of truth)
  2. Run: node scripts/path-codec.js --encode-all > my-encoded-paths.js
  3. Copy decoder + encoded paths into your project`);
  }
}

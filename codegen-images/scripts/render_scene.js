#!/usr/bin/env node
/**
 * render_scene.js - Generate raytraced test images
 * 
 * Usage:
 *   node render_scene.js --out test.png
 *   node render_scene.js --size 512 --scene rgb --out rgb_spheres.png
 *   node render_scene.js --size 256 --scene mirror --camera 0,2,5 --out mirror.png
 * 
 * Options:
 *   --size <n>           Width and height (default: 256)
 *   --width <n>          Width (overrides --size)
 *   --height <n>         Height (overrides --size)
 *   --scene <name>       Preset scene: default, mirror, rgb, single (default: default)
 *   --camera <x,y,z>     Camera position (default: 0,1.4,4)
 *   --lookat <x,y,z>     Look-at target (default: 0,0.8,-2)
 *   --checker <n>        Checkerboard scale (default: 8)
 *   --out <file>         Output filename (required)
 *   --list-scenes        Show available preset scenes
 * 
 * Requires: npm install @napi-rs/canvas
 */

let createCanvas;
try {
  createCanvas = require('@napi-rs/canvas').createCanvas;
} catch {
  createCanvas = require('canvas').createCanvas;
}
const fs = require('fs');

// Preset scenes: [radius, r, g, b, reflectivity, x, y, z]
const SCENES = {
  // Classic 4-sphere demo scene
  default: [
    [0.6, 0.9, 0.2, 0.3, 0.3, -1.0, 0.6, 0],      // red-pink left
    [0.5, 0.2, 0.8, 0.9, 0.4, 0.8, 0.5, 0.5],     // cyan right-front
    [0.8, 0.95, 0.95, 1.0, 0.85, 0.3, 0.8, -0.8], // white mirror center-back
    [0.4, 1.0, 0.9, 0.3, 0.2, -0.3, 0.4, 0.8],    // yellow front
  ],
  // Single large mirror sphere
  mirror: [
    [1.2, 0.98, 0.98, 1.0, 0.95, 0, 1.2, 0]
  ],
  // RGB spheres in a row
  rgb: [
    [0.55, 1.0, 0.15, 0.15, 0.25, -1.1, 0.55, 0],
    [0.55, 0.15, 1.0, 0.15, 0.25, 0, 0.55, 0],
    [0.55, 0.15, 0.15, 1.0, 0.25, 1.1, 0.55, 0],
  ],
  // Single orange sphere
  single: [
    [0.9, 0.95, 0.5, 0.15, 0.35, 0, 0.9, 0]
  ],
  // Metallic spheres
  metallic: [
    [0.7, 0.9, 0.8, 0.3, 0.7, -0.8, 0.7, 0],      // gold
    [0.7, 0.8, 0.8, 0.85, 0.8, 0.8, 0.7, 0],      // silver
  ],
};

function makeTestImage(W = 256, H = W, S, C, L, P) {
  const M = Math, A = M.abs, U = M.max;
  const m = e => U(0, M.min(1, e));
  const p = e => (t, l) => t.map((t, a) => e(t, l[a]));
  const i = (e, t) => e + t;
  const u = p(i);
  const R = p((e, t) => e - t);
  const o = p((e, t) => e * t);
  const c = (e, t) => e.map(e => e * t);
  const b = (e, t) => o(e, t).reduce(i);
  const g = e => c(e, 1 / (M.hypot(...e) || 1));
  const h = ([e, t, l]) => [t, l, e];
  const d = (e, t) => R(e, c(t, 2 * b(e, t)));
  
  C = C || [0, 1.4, 4];
  L = L || [0, 0.8, -2];
  P = P || (([x, , z]) => (8 * x & 1) ^ (8 * z & 1));
  S = S || SCENES.default;
  
  const w = g(R(L, C));
  const x = (e, t) => h(R(o(e, h(t)), o(h(e), t)));
  const y = g(x(w, [0, 1, 0]));
  const G = g(x(y, w));
  const V = g([-1, 1, 0.6]);
  
  const j = e => {
    let t = m(0.5 * (1 - b(e, V)));
    return [m(1 - 2 * t * t), m(1 - 2 * t), m(1 - t / 2)];
  };
  
  const v = (e, m) => {
    let p, s, t = 1e9, k = -1, n = [0, 1, 0];
    if (A(m[1]) > 1e-6) {
      let a = -e[1] / m[1];
      if (a > 1e-4) { t = a; k = 0; p = u(e, c(m, a)); }
    }
    for (let [r, ir, og, hb, dr, ...B] of S) {
      let q = R(e, B), w = b(q, m), x = w * w - (b(q, q) - r * r);
      if (x > 0) {
        let l = M.sqrt(x), bb = -w - l;
        if (bb < 1e-4) bb = -w + l;
        if (bb > 1e-4 && bb < t) {
          t = bb; k = 1; p = u(e, c(m, bb));
          n = g(R(p, B)); s = { c: [ir, og, hb], f: dr };
        }
      }
    }
    return k < 0 ? 0 : { t, k, p, n, s };
  };
  
  const z = (e, t) => {
    let a = [0, 0, 0], r = [1, 1, 1];
    for (let _ = 0; _ < 3; _++) {
      let Q = v(e, t);
      if (!Q) { let e = j(t); return u(a, o(r, e)); }
      let ii, hh, Z = Q.p, q = Q.n;
      if (Q.k === 0) {
        ii = P(Z) ? [0.92, 0.94, 0.98] : [0.48, 0.52, 0.58];
        hh = 0.1 + 0.38 * m(1 - A(t[1]));
      } else {
        ii = Q.s.c; hh = Q.s.f;
      }
      let xx = v(u(Z, c(q, 1e-4)), V)?.t < 20 ? 0.18 : 1;
      let yy = (xx ? 1 : 0) * U(0, b(q, g(R(V, t)))) ** (Q.k ? 120 : 70);
      let GG = u(c(ii, xx * (0.1 + 0.9 * U(0, b(q, V))) * (0.65 + 0.35 * q[1])),
                 c([1, 1, 1], yy * (Q.k ? 0.55 : 0.35) + 0.18 * U(0, 1 + b(t, q)) ** 2));
      a = u(a, o(r, GG));
      if (hh < 0.001) break;
      r = c(r, hh);
      e = u(Z, c(q, 1e-4));
      t = g(d(t, q));
    }
    return a;
  };
  
  // Create image data array
  const data = new Uint8ClampedArray(W * H * 4);
  
  for (let l = 0; l < H; l++) {
    let a = 0.4 * (1 - 2 * (l + 0.5) / H);
    for (let f = 0; f < W; f++) {
      let n = z(C, g(u(u(c(y, 0.4 * (2 * (f + 0.5) / W - 1) * (W / H)), c(G, a)), w)))
        .map(e => (e / (1 + e)) ** (1 / 2.2));
      n = (e => n.map(t => m(1.6875 * t - 0.4375 * e - 0.125)))(b(n, [0.2126, 0.7152, 0.0722]));
      let pp = (f + 0.5) / W - 0.5, ii = (l + 0.5) / H - 0.5;
      let k = m(1 - 0.85 * (pp * pp + ii * ii));
      n = c(n, k);
      let idx = 4 * (l * W + f);
      data[idx] = n[0] * 255;
      data[idx + 1] = n[1] * 255;
      data[idx + 2] = n[2] * 255;
      data[idx + 3] = 255;
    }
  }
  
  return { data, width: W, height: H };
}

function parseArgs(args) {
  const opts = {
    size: 256,
    width: null,
    height: null,
    scene: 'default',
    camera: null,
    lookat: null,
    checker: 8,
    out: null,
    listScenes: false,
  };
  
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    const next = args[i + 1];
    switch (arg) {
      case '--size': opts.size = parseInt(next); i++; break;
      case '--width': opts.width = parseInt(next); i++; break;
      case '--height': opts.height = parseInt(next); i++; break;
      case '--scene': opts.scene = next; i++; break;
      case '--camera': opts.camera = next.split(',').map(Number); i++; break;
      case '--lookat': opts.lookat = next.split(',').map(Number); i++; break;
      case '--checker': opts.checker = parseFloat(next); i++; break;
      case '--out': opts.out = next; i++; break;
      case '--list-scenes': opts.listScenes = true; break;
    }
  }
  return opts;
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
  
  if (opts.listScenes) {
    console.log('Available scenes:\n');
    for (const [name, spheres] of Object.entries(SCENES)) {
      console.log(`  ${name.padEnd(10)} ${spheres.length} sphere(s)`);
    }
    process.exit(0);
  }
  
  if (!opts.out) {
    console.error('Error: Must specify --out <filename>');
    process.exit(1);
  }
  
  const scene = SCENES[opts.scene];
  if (!scene) {
    console.error(`Unknown scene: ${opts.scene}`);
    console.error('Use --list-scenes to see available scenes');
    process.exit(1);
  }
  
  const W = opts.width || opts.size;
  const H = opts.height || opts.size;
  const checker = opts.checker;
  const planeTexture = ([x, , z]) => (checker * x & 1) ^ (checker * z & 1);
  
  console.log(`Rendering ${W}x${H} scene: ${opts.scene}...`);
  const start = Date.now();
  
  const img = makeTestImage(W, H, scene, opts.camera, opts.lookat, planeTexture);
  
  console.log(`Rendered in ${Date.now() - start}ms`);
  
  // Convert to PNG via canvas
  const canvas = createCanvas(W, H);
  const ctx = canvas.getContext('2d');
  const imageData = ctx.createImageData(W, H);
  imageData.data.set(img.data);
  ctx.putImageData(imageData, 0, 0);
  
  const buffer = canvas.toBuffer('image/png');
  fs.writeFileSync(opts.out, buffer);
  console.log(`Saved: ${opts.out}`);
}

main();

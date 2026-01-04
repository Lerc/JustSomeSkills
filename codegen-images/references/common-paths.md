# Common SVG Paths Library

> **Note:** After editing paths in this file, run `python3 scripts/update_sampler.py` to update the sampler.html preview.

**Centered at origin (0, 0)** with content spanning roughly -24 to +24 on each axis (48px content).

The `scale` parameter works intuitively since paths are centered at origin:
```javascript
// Default scale (1.0) fills a 64×64 canvas with 8px padding
simpleImage(path, 64, 64, opts);

// For other sizes, scale proportionally
simpleImage(path, 48, 48, { ...opts, scale: 48/64 });
simpleImage(path, 128, 128, { ...opts, scale: 2 });
```

## Usage

```javascript
const PATHS = { /* copy paths below */ };

// Default size (64×64)
const icon = simpleImage(PATHS.CHECK, 64, 64, { stroke: "#0a0", fill: "#0000", thickness: 4 });

// Different sizes - just use scale parameter
const small = simpleImage(PATHS.CHECK, 48, 48, { stroke: "#0a0", fill: "#0000", thickness: 3, scale: 48/64 });
```

## UI Icons

```javascript
const UI = {
  // Arrows (solid triangles)
  ARROW_RIGHT: "M-16 -20 L20 0 -16 20 Z",
  ARROW_LEFT: "M16 -20 L-20 0 16 20 Z",
  ARROW_UP: "M-20 16 L0 -20 20 16 Z",
  ARROW_DOWN: "M-20 -16 L0 20 20 -16 Z",

  // Chevrons (stroke-only, use fill:#0000)
  CHEVRON_RIGHT: "M-12 -20 L12 0 m 0 0 L-12 20",
  CHEVRON_LEFT: "M12 -20 L-12 0 m 0 0 L12 20",
  CHEVRON_UP: "M-20 12 L0 -12 m 0 0 L20 12",
  CHEVRON_DOWN: "M-20 -12 L0 12 m 0 0 L20 -12",

  // Common actions
  CLOSE: "M-20 -20 L20 20 M20 -20 L-20 20",
  CHECK: "M-22 2 L-6 18 m 0 0 L22 -18",
  PLUS: "M0 -22 L0 22 M-22 0 L22 0",
  MINUS: "M-22 0 L22 0",

  // Menu
  HAMBURGER: "M-22 -16 L22 -16 M-22 0 L22 0 M-22 16 L22 16",
  KEBAB: "M0 -22 L0 -18 m 0 0 M0 -2 L0 2 m 0 0 M0 18 L0 22",
  DOTS_H: "M-22 0 L-18 0 m 0 0 M-2 0 L2 0 m 0 0 M18 0 L22 0",

  // Media
  PLAY: "M-16 -22 L20 0 -16 22 Z",
  PAUSE: "M-18 -22 L-6 -22 -6 22 -18 22 Z M6 -22 L18 -22 18 22 6 22 Z",
  STOP: "M-20 -20 L20 -20 20 20 -20 20 Z",
  SKIP_FWD: "M-22 -20 L2 0 -22 20 Z M2 -20 L22 0 2 20 Z",
  SKIP_BACK: "M22 -20 L-2 0 22 20 Z M-2 -20 L-22 0 -2 20 Z",

  // Misc
  SEARCH: "M-4 -22 A18 18 0 1 0 -4 14 18 18 0 1 0 -4 -22 M10 10 L24 24",
  REFRESH: "M0 -24 A24 24 0 1 1 -24 0 A24 24 0 1 0 0 -24 L-5 -24 M1 -17 L-5 -24 L1 -32 L-5 -24",
  HOME: "M-24 -2 L0 -22 24 -2 24 22 6 22 6 6 -6 6 -6 22 -24 22 Z",
  GEAR: "M-2 -24 L2 -24 4 -18 10 -16 16 -20 19 -17 15 -10 17 -4 24 -2 24 2 18 4 16 10 20 16 17 19 10 15 4 17 2 24 -2 24 -4 18 -10 16 -16 20 -19 17 -15 10 -17 4 -24 2 -24 -2 -18 -4 -16 -10 -20 -16 -17 -19 -10 -15 -4 -17 Z M0 -8 A8 8 0 1 0 0 8 8 8 0 1 0 0 -8",
  STAR: "M0 -24 L6 -6 24 -6 10 6 16 24 0 14 -16 24 -10 6 -24 -6 -6 -6 Z",
  HEART: "M0 20 L-20 0 A12 12 0 0 1 0 -14 12 12 0 0 1 20 0 Z",

  // Edit
  PENCIL: "M12 -24 L24 -12 -8 20 -24 24 -20 8 Z M8 -20 L20 -8",
  TRASH: "M-12 -16 L12 -16 M-8 -16 L-8 -20 8 -20 8 -16 M-16 -12 L16 -12 12 24 -12 24 Z",
  COPY: "M-14 -20 L10 -20 10 12 -14 12 Z M-10 12 L-10 20 14 20 14 -12 10 -12",
};
```

## Electronics Symbols

```javascript
const ELECTRONICS = {
  // Logic gates (designed for horizontal signal flow, input left, output right)
  // Body spans roughly x:12-44, output at x:52
  
  AND_GATE: "M-20 -16 L-4 -16 A16 16 0 0 1 -4 16 L-20 16 Z M20 0 L12 0",
  OR_GATE: "M-20 -16 Q-8 -16 12 0 Q-8 16 -20 16 Q-8 0 -20 -16 M12 0 L20 0",
  NOT_GATE: "M-20 -16 L-20 16 L8 0 Z M8 0 A4 4 0 0 1 16 0 A4 4 0 0 1 8 0 M16 0 L20 0",
  NAND_GATE: "M-20 -16 L-4 -16 A16 16 0 0 1 -4 16 L-20 16 Z M12 0 A4 4 0 0 1 20 0 A4 4 0 0 1 12 0",
  NOR_GATE: "M-20 -16 Q-8 -16 12 0 Q-8 16 -20 16 Q-8 0 -20 -16 M12 0 A4 4 0 0 1 20 0 A4 4 0 0 1 12 0",
  XOR_GATE: "M-20 -16 Q-8 -16 10 0 Q-8 16 -20 16 Q-8 0 -20 -16 M-24 -16 Q-12 0 -24 16 Q-12 0 -24 -16 M10 0 L20 0",
  BUFFER: "M-20 -16 L-20 16 12 0 Z M12 0 L20 0",

  // Discrete components (vertical orientation)
  RESISTOR: "M0 -24 L0 -16 m 0 0 M0 -16 L-8 -12 m 0 0 M-8 -12 L8 -4 m 0 0 M8 -4 L-8 4 m 0 0 M-8 4 L8 12 m 0 0 M8 12 L0 16 m 0 0 M0 16 L0 24",
  RESISTOR_IEC: "M0 -24 L0 -12 m 0 0 M-8 -12 L8 -12 m 0 0 M8 -12 L8 12 m 0 0 M8 12 L-8 12 m 0 0 M-8 12 L-8 -12 m 0 0 M0 12 L0 24",
  CAPACITOR: "M0 -24 L0 -8 M-16 -8 L16 -8 M-16 8 L16 8 M0 8 L0 24",
  CAPACITOR_POL: "M0 -24 L0 -4 M-16 -4 L16 -4 M-16 4 Q0 -4 16 4 Q0 -4 -16 4 m 0 0 M0 0 L0 24 M10 -20 L18 -20 m 0 0 M14 -24 L14 -16",
  INDUCTOR: "M0 -24 L0 -16 m 0 0 M0 -16 A6 6 0 0 1 0 -4 A6 6 0 0 0 0 -16 m 0 0 M0 -4 A6 6 0 0 1 0 8 A6 6 0 0 0 0 -4 m 0 0 M0 8 A6 6 0 0 1 0 20 A6 6 0 0 0 0 8 m 0 0 M0 20 L0 24",
  DIODE: "M24 0 L12 0 m 0 -12 V12 M12 0 L-12 -12 V12 Z M-12 0 L-24 0",
  // LED: diode with emission arrows - tip-out pattern for fill-safety
  LED: "M-4 -20 L2 -22 M-6 -14 L2 -22 M8 -18 L7 -12 M2 -22 L1 -16 M2 -16 L8 -18 M1 -10 L8 -18 M24 0 H12 M12 -12 V12 M12 0 L-12 -12 V12 Z M-12 0 H-24",
  ZENER: "M24 0 L12 0 m 6 16 l-6 -4 M6 -16 l6 4 m 0 0 V12 M12 0 L-12 -12 V12 Z M-12 0 L-24 0",

  // Transistors - arrows use "tip-out" pattern with m 0 0 breaks for fill-safety
  // NMOS: gate left, source/drain vertical, arrows point outward (enhancement indicators)
  NMOS: "M-12 -12 V12 M7 -34 v22 m 0 0 H-4 m 0 -4 v8 m 0 4 V4 m 0 4 v8 m -8 -4 H-38 M7 34 V0 M7 0 H-4 m 0 12 L1 8 v8 Z M7 12 H1 M-4 23 A1 1 0 0 0 6 -23 A1 1 0 0 0 -4 23 A1 1 0 0 1 6 -23 A1 1 0 0 1 -4 23",
  // PMOS: same but arrows point inward, circle on gate (two semicircles for fill-safety)
  PMOS: "M-12 -12 V12 M7 -34 v22 m 0 0 H-4 m 0 -4 v8 m 0 4 V4 m 0 4 v8 m -8 -4 H-38 M7 34 V0 M7 0 H-4 m 11 12 L1 8 v8 Z M1 12 H-4 M-4 23 A1 1 0 0 0 6 -23 A1 1 0 0 0 -4 23 A1 1 0 0 1 6 -23 A1 1 0 0 1 -4 23",
  // NPN: emitter arrow points away from base (outward current flow)
  NPN: "M-6 16 L-2 8 L4 16 Z M-12 8 L-4 12 M4 16 L12 20 M12 -20 L-12 -8 m 0 32 V-24 M-28 0 h16",
  // PNP: emitter arrow points toward base (inward current flow)  
  PNP: "M2 20 l4 -8 H-4 Z M-12 8 l8 4 m 8 4 l8 4 M12 -20 L-12 -8 m 0 32 V-24 M-28 0 h16",

  // Power/Ground - VCC arrow uses tip-out pattern
  GND: "M0 -24 L0 -4 M-16 -4 L16 -4 M-10 4 L10 4 M-4 12 L4 12",
  VCC: "M0 24 L0 -12 M-12 4 L12 4 M0 -12 L-6 -4 m 0 0 M0 -12 L6 -4 m 0 0",
  POWER: "M0 -24 L0 -8 M-12 -8 L12 -8",
  
  // Connectors (circles as two semicircles)
  JACK: "M0 -16 A16 16 0 0 1 0 16 A16 16 0 0 1 0 -16 M0 -6 L0 6 M-6 0 L6 0",
  TERMINAL: "M0 -24 L0 -8 A8 8 0 0 1 0 8 A8 8 0 0 1 0 -8",
};
```

## Geometric Shapes

```javascript
const SHAPES = {
  // Regular polygons centered at origin with radius ~24
  TRIANGLE: "M0 -24 L24 18 -24 18 Z",
  SQUARE: "M-22 -22 L22 -22 22 22 -22 22 Z",
  DIAMOND: "M0 -24 L24 0 0 24 -24 0 Z",
  PENTAGON: "M0 -24 L24 -4 16 22 -16 22 -24 -4 Z",
  HEXAGON: "M-13 -20 L-24 0 L-13 20 H13 L24 0 L13 -20 Z",
  OCTAGON: "M-8 -24 L8 -24 24 -8 24 8 8 24 -8 24 -24 8 -24 -8 Z",

  // Circles (bezier approximation)
  CIRCLE: "M0 -24 C14 -24 24 -14 24 0 24 14 14 24 0 24 -14 24 -24 14 -24 0 -24 -14 -14 -24 0 -24 Z",
  RING: "M0 -24 C14 -24 24 -14 24 0 24 14 14 24 0 24 -14 24 -24 14 -24 0 -24 -14 -14 -24 0 -24 Z M0 -12 C-8 -12 -12 -6 -12 0 -12 8 -6 12 0 12 8 12 12 6 12 0 12 -8 6 -12 0 -12 Z",

  // Lines and crosses
  CROSS: "M0 -24 L0 24 M-24 0 L24 0",
  X: "M-20 -20 L20 20 M20 -20 L-20 20",
  CROSSHAIR: "M0 -28 L0 -16 M0 16 L0 28 M-28 0 L-16 0 M16 0 L28 0 M0 0 A4 4 0 1 0 0 0",
};
```

## Miscellaneous

```javascript
const MISC = {
  // Fishing hook (ping-pong Q curves with moves, not lines)
  HOOK: "M-8 -24 L-8 4 Q-8 20 8 20 Q-8 20 -8 4 m 0 0 M8 20 Q20 20 20 8 Q20 20 8 20 m 0 0 M20 8 L20 4",
  
  // Warning/info
  WARNING: "M0 -24 L24 20 -24 20 Z M0 -8 L0 6 M0 12 L0 14",
  INFO: "M0 -24 A24 24 0 1 0 0 -24 M0 -12 L0 -10 M0 -4 L0 16",
  
  // Brackets
  BRACKET_L: "M8 -24 L-8 -24 m 0 0 L-8 24 m 0 0 L8 24",
  BRACKET_R: "M-8 -24 L8 -24 m 0 0 L8 24 m 0 0 L-8 24",
  BRACE_L: "M8 -24 Q0 -24 0 -12 m 0 0 L0 -4 m 0 0 Q0 0 -8 0 m 0 0 Q0 0 0 4 m 0 0 L0 12 m 0 0 Q0 24 8 24",
  
  // Cursor/pointer
  CURSOR: "M-20 -24 L-20 16 -8 8 0 24 8 20 0 4 16 4 Z",
  HAND: "M-13 13 q-6 -6 -7 -13 q3 -8 8 8 h1 l-1 -20 c0 -8 7 -10 6 11 c-1 -23 5 -33 6 -4 l0.5 6 C0 -32 4 -34 6 -20 v14 l0.5 -4 C6 -29 10 -28 11 -23 c1 9 0 18 0 22 l1 -10 c0 -12 6 -5 5 10 L15 11 Q9 30 -13 13",
};
```

## Combining Paths

Multiple paths can be combined in a single string:

```javascript
// LED with rays - combine diode + ray marks
const ledWithRays = ELECTRONICS.LED;  // already includes rays

// Custom composite: circle with plus
const addButton = SHAPES.CIRCLE + " " + UI.PLUS;
simpleImage(addButton, 64, 64, { fill: "#4a4", stroke: "#fff", thickness: 3 });
```

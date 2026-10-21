# Fill-Safe Stroke-Only Paths

When rendering SVG paths, some environments call both `fill()` and `stroke()` on every path. This causes unintended fills in shapes meant to be stroke-only. To create paths that remain visually stroke-only even when filled, construct them with **zero enclosed area**.

## Lines: Break with `m 0 0`

A single line segment has no area. Insert `m 0 0` between segments to break the path into separate zero-area subpaths:

```
M0 0 L10 10 m 0 0 L20 0 m 0 0 L10 10
```

Each segment is isolated—fill() produces nothing visible.

## Cubic Bézier Curves (C): Ping-Pong Control Points

Trace the curve forward, then back with control points reversed. For points P1→P2→P3→P4, use order 1,2,3,4,3,2,1:

```
M P1 C P2 P3 P4 C P3 P2 P1 m 0 0 L P4
```

**Example:** Curve from (2,9) to (3,11) with control points (4,3) and (6,5):
```
M2 9 C4 3 6 5 3 11 C6 5 4 3 2 9 m 0 0 L3 11
```

The curve goes to (3,11) and returns to (2,9) via the same shape, enclosing zero area. The `m 0 0` breaks the path, then `L3 11` draws a visible line to the endpoint.

## Quadratic Bézier Curves (Q): Same Principle

For Q curves with control point P2: go P1→P2→P3, return P3→P2→P1:

```
M P1 Q P2 P3 Q P2 P1 m 0 0 L P3
```

**Example:**
```
M3 1 Q-3 -1.5 8 9 Q-3 -1.5 3 1 m 0 0 L8 9 m 0 0
```

## Arcs (A): Reverse the Sweep Flag

For arcs, keep radii and rotation the same, but flip the sweep flag (0↔1) and swap start/end points:

```
M P1 A rx ry rot large sweep P2 A rx ry rot large !sweep P1 m 0 0 L P2
```

**Example:** Arc from (5,2) to (7,3):
```
M5 2 A1.2 3.4 5.6 0 1 7 3 A1.2 3.4 5.6 0 0 5 2 m 0 0 L7 3
```

The first arc sweeps clockwise (flag=1), the return arc sweeps counter-clockwise (flag=0), enclosing zero area.

## Summary

| Element | Zero-Area Technique |
|---------|---------------------|
| Lines | Break with `m 0 0` between segments |
| C curves | Forward C(P2,P3,P4) then back C(P3,P2,P1) |
| Q curves | Forward Q(P2,P3) then back Q(P2,P1) |
| Arcs | Same arc params, flip sweep flag (0↔1) |

## Arrow Direction Clarity

When creating directional arrows (like refresh icons), make the direction clear by including a short segment in the pointing direction before the barbs spread:

```
// Unclear - barbs go directly diagonal from tip
M0 -24 L-8 -18 m 0 0 M0 -24 L-8 -30

// Clear - horizontal left segment establishes direction, then barbs spread
M0 -24 L-5 -24 L3 -15 m 0 0 M0 -24 L-5 -24 L3 -32
```

The bent arrow shape `tip → direction → barb` is more readable than `tip → barb` alone.

The `arrow-path.js` generator uses these techniques automatically when `headType: 'open'` is specified.

# codegen-images

Agent-facing instructions are in `SKILL.md`. This file is for people maintaining the skill.

## Layout

```
codegen-images/
├── SKILL.md                    simpleImage, path conventions, PNG output, index of references
├── sampler.html                Preview of every library path and the raytraced scenes
├── references/
│   ├── common-paths.md         Path library: the single source of truth for all paths
│   ├── fill-safe-paths.md      Zero-area techniques for stroke-only paths
│   ├── arrow-generator.md      arrow-path.js usage
│   ├── path-encoding.md        Compact path codec
│   └── test-images.md          makeTestImage raytracer and render_scene.js
└── scripts/
    ├── path-codec.js           Encode/decode paths; loadPathLibrary() parses common-paths.md
    ├── save_png.js             Render a path to PNG (presets come from common-paths.md)
    ├── render_scene.js         Render a raytraced scene to PNG
    ├── arrow-path.js           Generate arrow paths
    └── update_sampler.py       Regenerate sampler.html's PATHS from common-paths.md
```

## Adding or changing a path

1. Edit `references/common-paths.md`. Keep paths origin-centered within about ±24, and make stroke-only shapes zero-area (see `fill-safe-paths.md`).
2. Run `python3 scripts/update_sampler.py`, then open `sampler.html` to check the result.

`save_png.js --preset` and `path-codec.js --encode-all` read the library directly, so they need no update.

## Requirements

Node.js for the scripts (`@napi-rs/canvas` for PNG output), and Python 3 for `update_sampler.py`.

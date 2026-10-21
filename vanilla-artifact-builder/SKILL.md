---
name: vanilla-artifact-builder
description: Develops a vanilla HTML/CSS/JavaScript page as separate source files, then bundles them (images included) into one self-contained HTML file that embeds its own recoverable sources. Use when the user asks for a single-file HTML deliverable, when the environment can only display or deliver one self-contained HTML file but the page is large enough to benefit from separate files, or when given an HTML bundle containing a VANILLA-ARTIFACT-SOURCE-MAP-V1 comment whose sources should be extracted.
---

# Vanilla Artifact Builder

Develop in `<project>/src/` as an ordinary static site, then bundle it into one
HTML file. The bundle ends with a comment holding every source file
(LZMA-compressed, base64-encoded), so it can be unbundled back to `src/` later,
by you or by anyone who has the bundle.

## When this fits

Use it when the deliverable must be **one self-contained HTML file**: the user
asked for that, or the environment displays or delivers only single HTML files
(for example, a sandbox whose outputs render as claude.ai artifacts). When the
environment can publish a multi-file page directly, publish the files as they
are, unless the user asked for a single file. A page small enough to write as
one file needs no bundler.

## Setup

Resolve `<skill-dir>` as the directory containing this `SKILL.md`, and run
scripts by their absolute paths. They take paths as arguments and work from any
current directory.

1. Run `<skill-dir>/scripts/check-environment.sh` once per environment. Each
   line is PASS or FAIL with a remedy; exit 0 means the skill is usable. It
   runs a real init → bundle → unbundle round trip, which needs npm registry
   access on first run (`--quick` checks tools only).
2. Set `VANILLA_ARTIFACT_OUTPUT_DIR` to the directory your environment delivers
   files from (on claude.ai, `/mnt/user-data/outputs`). Leave it unset to write
   bundles into the project directory.

Requirements: Node.js with npm/npx, and Python 3 with `lzma`. The first bundle
installs Parcel into the project's `node_modules/`.

## Workflow

```bash
<skill-dir>/scripts/init-vanilla-artifact.sh <project-dir>     # starter src/
# edit <project-dir>/src/ ...
<skill-dir>/scripts/bundle-vanilla-artifact.sh <project-dir>   # build + inline
```

- `src/index.html` is the entry point. Reference other files by relative path
  (`./styles.css`, `./images/logo.png`); ES module imports and multiple
  scripts work, since Parcel bundles them.
- Images go in `src/images/` (PNG, JPEG, GIF, SVG, WebP). They are inlined as
  data URLs in the page and stored in the source map.
- The bundle is named after the project directory: `<name>.html`, or
  `<name>-<v>.html` with `-v <v>` to keep earlier versions side by side.
- `--with-source` also copies `src/` to `<output-dir>/<name>-source/`: the
  editable sources, without the build scaffolding (`node_modules/`, `dist/`,
  configs), which stays in the project directory.
- CDN `<script>`/`<link>` URLs are left as references. Whether they load
  depends on where the page is viewed.

Open the bundle in a browser, or deliver it through your environment, and check
it before handing it over.

## Unbundling

```bash
<skill-dir>/scripts/unbundle-vanilla-artifact.sh <bundle.html> [<project-dir>/src]
```

Writes every embedded file (default `./src`). Then edit and re-bundle the
project directory as above. Bundles made before LZMA compression still unbundle.

## Scripts

| Script | Purpose |
|---|---|
| `check-environment.sh [--quick]` | Verify this environment can use the skill |
| `init-vanilla-artifact.sh <dir>` | Create a starter project |
| `bundle-vanilla-artifact.sh [-v V] [--with-source] [dir]` | Build, inline and embed sources |
| `unbundle-vanilla-artifact.sh <bundle> [out]` | Recover sources from a bundle |
| `inline_html.py <dist/index.html>` | Inline scripts, styles and images (used by the bundler) |

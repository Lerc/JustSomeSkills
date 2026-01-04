---
name: vanilla-artifact-builder
description: Create claude.ai HTML artifacts from separate HTML, CSS, and JavaScript files. Use when users want to work with vanilla JavaScript in separate files but need them bundled into a single HTML artifact for rendering in Claude's interface. Supports unbundling to extract original source files. When sharing source files with users, provide ONLY the actual source files (*.html, *.css, *.js), never the build directory or node_modules. Not needed for simple single-file HTML artifacts.
---

# Vanilla Artifact Builder

Build vanilla JavaScript claude.ai artifacts using a clean workflow that keeps HTML, CSS, and JavaScript in separate files during development, then bundles them into a single HTML artifact for display. Supports round-trip unbundling to extract source files from bundled artifacts.

## Workflow

1. Initialize the project using `scripts/init-vanilla-artifact.sh` (creates `src/` directory)
2. Develop your artifact by editing files in the `src/` directory
3. Optionally add images to `src/images/`
4. Bundle with `scripts/bundle-vanilla-artifact.sh` (bundles everything in `src/`)
5. Display artifact to user
6. (Optional) Extract source files using `scripts/unbundle-vanilla-artifact.sh` (recreates `src/` directory)

**Stack**: Vanilla JavaScript + HTML + CSS + Parcel (bundling) + html-inline + source metadata

**Key Principle**: The `src/` directory is the **ground truth** for what gets bundled. Everything in `src/` (HTML, CSS, JS, and images) is included in the bundle and metadata.

## Critical Best Practices

**The src/ directory is the single source of truth:**

All development happens in the `src/` directory:
```
project/
├── src/              ← Everything here gets bundled
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│   └── images/       ← Place images here
│       └── logo.png
├── bundle.html       ← Generated artifact
├── dist/             ← Build output (temporary)
├── node_modules/     ← Dependencies (temporary)
└── .gitignore
```

**When sharing files with users:**

✅ **Share the src/ directory** - Contains all editable source files
- HTML, CSS, JS files
- Images in images/ subdirectory
- Works as a static website when opened locally
- Typical size: <50KB even with small images

✅ **Share bundle.html** - The single-file artifact

❌ **NEVER share:**
- dist/ directory (build output, not source)
- node_modules/ directory (40MB+ of dependencies)
- .parcel-cache/ directory
- package.json or build configuration files
- Compressed archives of the entire project directory

**Simple rule**: Share only what's in `src/` plus the `bundle.html` artifact. Everything else is temporary build infrastructure.

## When to Use This Skill

Use this skill when:
- User wants separate HTML, CSS, and JS files for better code organization
- Creating interactive vanilla JavaScript artifacts
- Building artifacts that would benefit from modular file structure
- User wants to extract/edit source files from a bundled artifact

Do NOT use this skill when:
- User requests a simple single-file HTML artifact (create directly instead)
- User requests React/TypeScript artifacts (use artifacts-builder skill instead)
- Artifact is trivial and doesn't benefit from separate files

## Quick Start

### Step 1: Initialize Project

Run the initialization script to create a new vanilla JS project:
```bash
bash scripts/init-vanilla-artifact.sh <project-name>
cd <project-name>
```

This creates a project with clear separation between source and build:

```
project-name/
├── src/                    ← All source files (ground truth)
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│   └── images/             ← Place image files here
│       └── README.md
└── .gitignore
```

**After building, additional files appear:**
```
project-name/
├── src/                    ← Your source files (permanent)
├── bundle.html             ← Generated artifact (shareable)
├── dist/                   ← Build output (temporary, ignored)
├── node_modules/           ← Dependencies (temporary, ignored)
├── package.json            ← Build config (temporary, ignored)
└── .parcelrc               ← Build config (temporary, ignored)
```

The `.gitignore` ensures build artifacts don't get committed to version control.

### Step 2: Develop Your Artifact

Edit the files in the `src/` directory to build your artifact:

**Source files (`src/`):**
- **index.html** - Structure and content
- **styles.css** - All styling (modern CSS supported)
- **script.js** - JavaScript logic and interactivity
- **Additional files** - Add more .html, .css, or .js files as needed

**Images (`src/images/`):**
- Place any image files here (PNG, JPEG, GIF, SVG, WebP)
- Reference them in HTML: `<img src="./images/logo.png">`
- Images are automatically:
  - Bundled into the artifact by Parcel
  - Base64-encoded in the source metadata
  - Extractable when unbundling

The files use normal HTML structure with relative paths:
```html
<link rel="stylesheet" href="./styles.css">
<img src="./images/logo.png">
<script src="./script.js"></script>
```

Everything in `src/` works as a standalone static website - open `src/index.html` in a browser to preview.

### Step 3: Bundle to Single HTML File

To bundle into a single HTML artifact:
```bash
bash scripts/bundle-vanilla-artifact.sh
```

**Optional versioning:**
```bash
bash scripts/bundle-vanilla-artifact.sh -v v1
bash scripts/bundle-vanilla-artifact.sh -v v2
bash scripts/bundle-vanilla-artifact.sh --version beta
```

This creates versioned bundles (e.g., `bundle-v1.html`, `bundle-v2.html`) allowing you to:
- Keep multiple versions for comparison
- Iterate without overwriting previous versions
- Share specific versions with users
- Track evolution of the artifact

Without a version flag, creates `bundle.html` (overwrites previous).

**Performance optimization:**
- First run installs dependencies (~10 seconds)
- Subsequent runs skip installation (~1 second)
- Only builds and bundles, much faster for iteration

This creates a self-contained artifact with everything from `src/` inlined, plus embedded source metadata.

**Requirements**: Run from project root (directory containing `src/`). The `src/` directory must contain `index.html`.

**What the script does**:
- Scans the entire `src/` directory
- Collects all HTML, CSS, and JS files
- Collects all image files from `src/images/`
- Skips dependency installation if already present
- Builds with Parcel (from `src/index.html`)
- Inlines all assets into single HTML
- Embeds concise source metadata with:
  - Skill identification
  - Format version marker  
  - Base64-encoded files (preserving directory structure)
  - Binary support for images
- Lists all bundle versions if using versioning

**What gets bundled**:
- All *.html, *.css, *.js files in `src/`
- All images in `src/images/` (PNG, JPEG, GIF, SVG, WebP)
- Directory structure preserved in metadata (e.g., "images/logo.png")

### Step 4: Share Artifact with User

Share the bundled HTML file with the user by copying it to `/mnt/user-data/outputs/` so they can view it as an artifact.

**IMPORTANT - When sharing source files:**

If the user requests the unbundled/source files, share ONLY the `src/` directory:

```bash
# Copy the entire src/ directory
cp -r src /mnt/user-data/outputs/project-name-source
```

**✅ The src/ directory contains:**
- index.html, styles.css, script.js
- Any additional .html, .css, or .js files
- images/ subdirectory with all images
- Everything needed as a working static website

**❌ NEVER share:**
- dist/ directory (build output, not source)
- node_modules/ directory (40MB+ dependencies)
- .parcel-cache/ directory (build cache)
- package.json, package-lock.json (build config)
- .parcelrc (build config)  
- bundle.html separately (share OR the src/, not both bundled together)

**Best practice:** The `src/` directory is self-contained and works immediately:
- Users can open `src/index.html` in any browser
- All relative paths work correctly
- Images display properly
- No build process needed to view
- Can be re-bundled if user has the skill

Typical `src/` directory size: <50KB even with small images, NOT 40MB+!

### Step 5: Unbundle (Optional)

To extract the original source files from a bundled artifact:

```bash
bash scripts/unbundle-vanilla-artifact.sh <bundle.html> [output-directory]
```

**Example:**
```bash
bash scripts/unbundle-vanilla-artifact.sh bundle.html ./my-project-src
```

Default output directory is `./src` if not specified.

This extracts all original source files from the bundle metadata, recreating the `src/` directory structure:

**What gets extracted:**
- All HTML, CSS, JS files (preserving any subdirectories)
- All images from `src/images/` (as binary files)
- Directory structure maintained (e.g., images/logo.png)

**The extracted src/ directory:**
- Works immediately as a static website
- Open index.html in browser to view
- Edit files with any text editor
- Re-bundle by running the bundle script from parent directory

**What the script does**:
- Validates bundle contains source metadata
- Extracts embedded JSON manifest
- Decodes base64-encoded files (text and binary)
- Recreates directory structure
- Writes all files to output directory

**Note**: Only works with bundles created using bundle-vanilla-artifact.sh that embeds source metadata. The unbundle script handles both text files (HTML/CSS/JS) and binary files (images) correctly.

## Development Tips

### Modular Code Organization

Structure your JavaScript for clarity:
```javascript
// State
let count = 0;

// DOM elements
const button = document.getElementById('myButton');
const output = document.getElementById('output');

// Functions
function updateDisplay() {
    output.textContent = `Count: ${count}`;
}

function handleClick() {
    count++;
    updateDisplay();
}

// Event listeners
button.addEventListener('click', handleClick);

// Initialize
updateDisplay();
```

### Multiple JavaScript Files

You can split your JavaScript into multiple files:
```html
<!-- In index.html -->
<script src="./utils.js"></script>
<script src="./config.js"></script>
<script src="./script.js"></script>
```

All files will be:
1. Bundled into the single HTML artifact
2. Preserved in the source metadata for unbundling

### External Resources

Can use CDN resources in HTML:
```html
<!-- Icons -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

<!-- Libraries -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

### Modern JavaScript Features

All modern JavaScript is supported:
- ES6+ syntax (arrow functions, destructuring, template literals)
- Async/await
- Modules (if using import/export, Parcel handles bundling)
- Web APIs (Fetch, LocalStorage, Canvas, etc.)

Note: Browser storage APIs work during development but remember artifacts run in a sandboxed environment where localStorage/sessionStorage may not persist.

## Round-Trip Workflow

The skill supports a complete round-trip editing workflow:

1. **Bundle** → Create artifact from source files
2. **Share** → User views artifact in Claude interface
3. **Unbundle** → Extract source files from artifact
4. **Edit** → Make improvements to source files
5. **Re-bundle** → Create updated artifact
6. **Share** → User views improved artifact

This enables iterative development and easy maintenance of artifacts.

## Self-Documenting Bundles

Bundles created with this skill include a concise metadata comment at the end:

```html
<!-- Metadata generated by the 'vanilla-artifact-builder' skill for Claude and can be interpreted by the same skill. VANILLA-ARTIFACT-SOURCE-MAP-V1 {...} -->
```

This annotation:
- Identifies what created the bundle
- Notes that the same skill can process it
- Contains the version marker and source map in one line
- Keeps the bundle size minimal while preserving source files

When users encounter a bundle, they can upload it to Claude and ask to extract the source files. Claude will recognize the metadata and use the unbundle script automatically.

## Iteration Workflow

The skill supports rapid iteration with versioning:

**First iteration:**
```bash
# Edit src/ files
bash bundle-vanilla-artifact.sh -v v1
# Creates bundle-v1.html
# Share with user
```

**Get feedback, make improvements:**
```bash
# Edit src/ files based on feedback
bash bundle-vanilla-artifact.sh -v v2
# Creates bundle-v2.html (v1 still exists)
# Share new version
```

**Benefits of versioned bundles:**
- Compare versions side-by-side
- Roll back if needed
- Show evolution to stakeholders
- Keep working versions during experimentation
- Fast: ~1 second after first build (dependencies cached)

**Version naming suggestions:**
- Sequential: v1, v2, v3
- Descriptive: beta, final, updated
- Dated: 2024-10-19, oct19
- Feature-based: with-images, responsive

**Sharing versioned bundles:**
```bash
# Share specific version
cp bundle-v2.html /mnt/user-data/outputs/artifact-v2.html

# Share all versions for comparison
cp bundle-v*.html /mnt/user-data/outputs/

# Share latest with generic name
cp bundle-v2.html /mnt/user-data/outputs/my-artifact.html
```

The `.gitignore` doesn't exclude bundle files, so versioned bundles can be tracked in version control if desired.

## Common Patterns

### Interactive Visualizations
Separate concerns for data, rendering, and interaction.

### Form-Based Applications
Keep validation logic, state management, and UI updates in separate functions.

### Games and Animations
Use requestAnimationFrame, separate game loop from rendering logic.

### Data Dashboards
Fetch data, process it, and render visualizations with clean separation.

## Troubleshooting

**Build fails**: Ensure index.html exists in project root and properly links to CSS/JS files.

**Bundled file too large**: Consider optimizing images, minifying code, or splitting into multiple artifacts.

**JavaScript not working**: Check browser console in bundled file. Ensure proper event listener setup and DOM element selection.

**Styling issues**: Verify CSS selectors match HTML structure. Check for specificity conflicts.

**Unbundle fails with "No source metadata found"**: The bundle was created with an older version of the bundling script. Only bundles created with the updated script contain metadata.

**Unbundled files don't match originals**: This should never happen. If it does, it indicates a bug in the base64 encoding/decoding process.

**User received 40MB+ tar.gz with node_modules**: This is incorrect! Never share the entire project directory. Only share the actual source files (*.html, *.css, *.js). The dist/, node_modules/, and build configuration files should never be shared with users. See "Step 4: Share Artifact with User" for correct file sharing practices.

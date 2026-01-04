# File Sharing Guide for vanilla-artifact-builder

## The Problem

When creating artifacts with vanilla-artifact-builder, the build process creates many files and directories. Users should NEVER receive the entire project directory - it can be 40MB+ with unnecessary build files.

## Directory Structure After Building

After running the bundle script, your project directory looks like this:

```
my-project/
├── index.html          ✅ Source file - SHARE THIS
├── styles.css          ✅ Source file - SHARE THIS
├── script.js           ✅ Source file - SHARE THIS
├── utils.js            ✅ Source file - SHARE THIS (if exists)
├── bundle.html         ✅ Artifact - SHARE THIS
├── dist/               ❌ Build output - DON'T SHARE
│   ├── index.html
│   ├── *.css
│   └── *.js
├── node_modules/       ❌ 40MB+ dependencies - DON'T SHARE
│   └── (158 packages)
├── .parcel-cache/      ❌ Build cache - DON'T SHARE
├── package.json        ❌ Build config - DON'T SHARE
├── package-lock.json   ❌ Build config - DON'T SHARE
└── .parcelrc           ❌ Build config - DON'T SHARE
```

## What to Share

### Scenario 1: User Wants the Artifact
**Share:** Just `bundle.html`

```bash
cp bundle.html /mnt/user-data/outputs/my-artifact.html
```

✅ User gets a single, self-contained HTML file  
✅ Works in Claude's artifact viewer  
✅ Contains embedded source metadata for unbundling  

### Scenario 2: User Wants Source Files
**Share:** Only the original source files

```bash
# Create a clean directory with just source files
mkdir -p /mnt/user-data/outputs/my-project-source
cp *.html *.css *.js /mnt/user-data/outputs/my-project-source/

# Or more specifically:
cp index.html styles.css script.js /mnt/user-data/outputs/my-project-source/
```

✅ User gets only editable files  
✅ Can open index.html directly in browser  
✅ Can edit with any text editor  
✅ Can re-bundle if they have the skill  
✅ Total size: typically < 10KB  

### Scenario 3: User Wants Both
**Share:** The artifact AND the source files separately

```bash
# The artifact
cp bundle.html /mnt/user-data/outputs/my-artifact.html

# The source files  
mkdir -p /mnt/user-data/outputs/my-artifact-source
cp *.html *.css *.js /mnt/user-data/outputs/my-artifact-source/
```

## What NOT to Share

❌ **NEVER do this:**
```bash
# BAD - includes 40MB+ of node_modules
tar -czf /mnt/user-data/outputs/my-project.tar.gz my-project/

# BAD - includes build artifacts
cp -r my-project /mnt/user-data/outputs/
```

❌ **NEVER share:**
- `dist/` directory
- `node_modules/` directory  
- `.parcel-cache/` directory
- `package.json` or `package-lock.json`
- `.parcelrc`
- Any tar.gz/zip of the entire project

## Why This Matters

**User receives wrong files:**
- 40MB+ download instead of <10KB
- Confusing directory structure
- Files they can't use (node_modules)
- Build artifacts instead of sources

**User receives correct files:**
- Minimal download size
- Clean, understandable structure
- Files work as static website
- Easy to edit and modify

## The Source Files Should Work Standalone

When you share source files, they should work as a complete, self-contained static website:

**Test this:**
```bash
# After extracting source files
cd my-project-source
# Open in browser
open index.html  # or double-click in file manager
```

✅ The page should display correctly  
✅ All styles should work  
✅ All JavaScript should work  
✅ No build process required  

This is because the source files use normal HTML structure:
```html
<link rel="stylesheet" href="./styles.css">
<script src="./script.js"></script>
```

## Quick Reference

| User Request | Share | Don't Share | Size |
|-------------|-------|-------------|------|
| "Can I have the artifact?" | bundle.html | Everything else | ~5KB |
| "Can I have the source?" | *.html, *.css, *.js | dist/, node_modules/, configs | ~10KB |
| "Can I have both?" | bundle.html + source files | dist/, node_modules/, configs | ~15KB |
| ❌ WRONG | entire directory as tar.gz | N/A | 40MB+ |

## Commands to Use

**Correct approach:**
```bash
# Share artifact
cp bundle.html /mnt/user-data/outputs/artifact.html

# Share source files (clean)
mkdir -p /mnt/user-data/outputs/source
cp index.html styles.css script.js /mnt/user-data/outputs/source/

# Or all HTML/CSS/JS files if you have multiple
cp *.html *.css *.js /mnt/user-data/outputs/source/
```

**Incorrect approach:**
```bash
# ❌ Don't do this
tar -czf output.tar.gz entire-project/
cp -r entire-project /mnt/user-data/outputs/
```

## Summary

- ✅ Share: Clean source files OR bundled artifact
- ❌ Never: node_modules, dist, build configs, or entire project directory  
- 🎯 Goal: Users get minimal, usable files that work immediately
- 📏 Size: Source files should be <10KB, not 40MB+

The build infrastructure is temporary scaffolding. Users only need the final artifact or the original source files - never the scaffolding itself.

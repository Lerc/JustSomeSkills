#!/usr/bin/env python3
"""
Update sampler.html with encoded paths from common-paths.md

This script:
1. Reads paths from references/common-paths.md
2. Encodes them using the Node.js path-codec.js encoder
3. Updates the PATHS section in sampler.html with the encoded paths
"""

import subprocess
import re
from pathlib import Path

# File paths
SKILL_DIR = Path("/mnt/skills/user/codegen-images")
COMMON_PATHS_MD = SKILL_DIR / "references" / "common-paths.md"
SAMPLER_HTML = SKILL_DIR / "sampler.html"
PATH_CODEC_JS = SKILL_DIR / "scripts" / "path-codec.js"

def encode_paths():
    """Run the Node.js encoder to generate encoded paths JavaScript"""
    try:
        result = subprocess.run(
            ["node", str(PATH_CODEC_JS), "--encode-all"],
            capture_output=True,
            text=True,
            check=True,
            cwd=str(SKILL_DIR)
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running encoder: {e}")
        print(f"stderr: {e.stderr}")
        raise

def extract_paths_section(encoded_output):
    """Extract just the PATHS object from the encoder output"""
    # Split by double newline to separate sections
    lines = encoded_output.split('\n')
    
    # Find the decoder line (starts with "function Q")
    decoder_line = None
    decoder_comment = None
    paths_start = None
    
    for i, line in enumerate(lines):
        if line.startswith('// Path decoder'):
            decoder_comment = line
        elif line.startswith('function Q'):
            decoder_line = line
        elif line.startswith('// Encoded paths'):
            paths_start = i
            break
    
    if not decoder_line or not decoder_comment or paths_start is None:
        raise ValueError("Could not find decoder and paths sections in encoded output")
    
    # Build decoder section (comment + function + blank line)
    decoder_section = f"{decoder_comment}\n{decoder_line}\n"
    
    # Build paths section (from "// Encoded paths" to end of const PATHS = {...})
    paths_lines = []
    in_paths = False
    brace_count = 0
    
    for i in range(paths_start, len(lines)):
        line = lines[i]
        paths_lines.append(line)
        
        if 'const PATHS = {' in line:
            in_paths = True
            brace_count = line.count('{') - line.count('}')
        elif in_paths:
            brace_count += line.count('{') - line.count('}')
            if brace_count == 0 and line.strip() == '};':
                break
    
    paths_section = '\n'.join(paths_lines)
    
    return decoder_section, paths_section

def update_sampler_html(decoder_section, paths_section):
    """Update the sampler.html file with new encoded paths and simplify rendering"""
    with open(SAMPLER_HTML, 'r') as f:
        content = f.read()
    
    # Pattern to match from "// Path decoder" comment through the end of "const PATHS = {...};"
    # This is more flexible and handles the exact format in the file
    pattern = re.compile(
        r'// Path decoder.*?\nfunction Q\(\[e\]\)\{.*?\}\n'
        r'// Encoded paths.*?\n'
        r'// To regenerate:.*?\n'
        r'const PATHS = \{.*?\n\};',
        re.DOTALL
    )
    
    # Build replacement string - need to escape backslashes for regex replacement
    # In regex replacement strings, backslashes are special, so we need to double them
    replacement = decoder_section.rstrip() + '\n' + paths_section
    # Escape backslashes for regex replacement (\ becomes \\)
    replacement = replacement.replace('\\', '\\\\')
    
    new_content, count = pattern.subn(replacement, content)
    
    if count == 0:
        raise ValueError("Could not find PATHS section in sampler.html")
    
    if count > 1:
        raise ValueError(f"Found multiple PATHS sections ({count}) in sampler.html")
    
    # Also update the getOpts function to render all paths with the same stroke and fill
    # Replace the entire getOpts function with a simplified version
    getopts_pattern = re.compile(
        r'// Rendering options based on icon type\n'
        r'const STROKE_KEYS = \[.*?\];\n'
        r'const DOT_KEYS = \[.*?\];\n'
        r'\n'
        r'function getOpts\(name, size\) \{.*?\n\}',
        re.DOTALL
    )
    
    simplified_getopts = '''// Rendering options - all paths use the same stroke and fill
function getOpts(name, size) {
  const baseThickness = size / 32;
  return { fill: "#e8e8ff", stroke: "#333", thickness: Math.max(1, baseThickness) };
}'''
    
    new_content, getopts_count = getopts_pattern.subn(simplified_getopts, new_content)
    
    if getopts_count == 0:
        print("⚠ Warning: Could not find getOpts function to update")
    else:
        print(f"✓ Updated getOpts function to use uniform rendering")
    
    with open(SAMPLER_HTML, 'w') as f:
        f.write(new_content)
    
    print(f"✓ Updated {SAMPLER_HTML}")
    print(f"  Replaced {count} PATHS section(s)")

def main():
    print("Updating sampler.html from common-paths.md...")
    print(f"  Source: {COMMON_PATHS_MD}")
    print(f"  Target: {SAMPLER_HTML}")
    
    # Check that files exist
    if not COMMON_PATHS_MD.exists():
        raise FileNotFoundError(f"Source file not found: {COMMON_PATHS_MD}")
    if not SAMPLER_HTML.exists():
        raise FileNotFoundError(f"Target file not found: {SAMPLER_HTML}")
    if not PATH_CODEC_JS.exists():
        raise FileNotFoundError(f"Encoder script not found: {PATH_CODEC_JS}")
    
    # Encode paths
    print("\nEncoding paths...")
    encoded_output = encode_paths()
    
    # Extract sections
    print("Extracting PATHS section...")
    decoder_section, paths_section = extract_paths_section(encoded_output)
    
    # Update sampler.html
    print("Updating sampler.html...")
    update_sampler_html(decoder_section, paths_section)
    
    print("\n✓ Update complete!")

if __name__ == "__main__":
    main()

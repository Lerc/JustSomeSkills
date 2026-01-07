#!/bin/bash
set -e

# Check if bundle file provided
if [ -z "$1" ]; then
  echo "❌ Error: No bundle file provided"
  echo "Usage: bash unbundle-vanilla-artifact.sh <bundle.html> [output-directory]"
  exit 1
fi

BUNDLE_FILE="$1"
OUTPUT_DIR="${2:-./src}"

# Check if bundle file exists
if [ ! -f "$BUNDLE_FILE" ]; then
  echo "❌ Error: Bundle file not found: $BUNDLE_FILE"
  exit 1
fi

echo "📂 Unbundling vanilla JS artifact..."
echo "   Source: $BUNDLE_FILE"
echo "   Output: $OUTPUT_DIR"

# Extract the source map from HTML comments
echo "🔍 Looking for source metadata..."

# Check if file contains the source map marker
if ! grep -q "VANILLA-ARTIFACT-SOURCE-MAP-V1" "$BUNDLE_FILE"; then
  echo "❌ Error: No source metadata found in bundle file."
  echo "   This file may not have been created with the bundle-vanilla-artifact-v2.sh script."
  echo "   Or it might be using an older bundling format."
  exit 1
fi

# Extract the JSON between the marker and end of comment
# Format: <!-- ... VANILLA-ARTIFACT-SOURCE-MAP-V1 {...} -->
SOURCE_MAP=$(grep -o 'VANILLA-ARTIFACT-SOURCE-MAP-V1 {.*}' "$BUNDLE_FILE" | sed 's/VANILLA-ARTIFACT-SOURCE-MAP-V1 //')

if [ -z "$SOURCE_MAP" ]; then
  echo "❌ Error: Could not extract source metadata."
  exit 1
fi

# Verify it looks like JSON
if ! echo "$SOURCE_MAP" | grep -q '^{.*}$'; then
  echo "❌ Error: Extracted data doesn't appear to be valid JSON."
  echo "   Data extracted: ${SOURCE_MAP:0:100}..."
  exit 1
fi

echo "✅ Found source metadata"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Parse the JSON and extract files
echo "📝 Extracting source files..."

# Use Python to parse JSON and decode base64 (with optional LZMA decompression)
python3 << PYTHON_SCRIPT
import json
import base64
import lzma
import os
import sys

def decode_content(encoded_content):
    """Decode base64 content, trying LZMA decompression first for backwards compatibility."""
    decoded_base64 = base64.b64decode(encoded_content)
    try:
        # Try LZMA decompression (new format)
        return lzma.decompress(decoded_base64)
    except lzma.LZMAError:
        # Not LZMA compressed, return raw data (backwards compatibility)
        return decoded_base64

try:
    source_map = json.loads('''$SOURCE_MAP''')
    output_dir = "$OUTPUT_DIR"
    
    for filename, encoded_content in source_map.items():
        # Handle subdirectories (e.g., images/logo.png)
        output_path = os.path.join(output_dir, filename)
        
        # Create parent directories if needed
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Decode content (handles both LZMA-compressed and raw base64)
        decoded_content = decode_content(encoded_content)
        
        # Write as binary to handle both text and image files
        with open(output_path, 'wb') as f:
            f.write(decoded_content)
        
        print(f"   ✓ {filename}")
    
    print(f"\n✅ Successfully extracted {len(source_map)} file(s) to {output_dir}")
    
except json.JSONDecodeError as e:
    print(f"❌ Error: Invalid JSON in source metadata: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
PYTHON_SCRIPT

if [ $? -eq 0 ]; then
  echo ""
  echo "🎉 Unbundle complete! Source files are ready for editing."
  echo ""
  echo "The files are in the src/ directory structure."
  echo "You can open $OUTPUT_DIR/index.html in a browser to view locally."
  echo ""
  echo "Next steps:"
  echo "1. Edit the extracted files in $OUTPUT_DIR"
  echo "2. Run bundle script from parent directory to re-bundle"
else
  echo "❌ Unbundling failed."
  exit 1
fi

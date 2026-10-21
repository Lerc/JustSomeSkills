#!/bin/bash
# Recover the source files embedded in a bundle made by bundle-vanilla-artifact.sh.
#
# Usage: unbundle-vanilla-artifact.sh <bundle.html> [OUTPUT_DIR]
#
#   OUTPUT_DIR  Where to write the files (default: ./src). Re-bundle by
#               running the bundle script on OUTPUT_DIR's parent.
set -e

if [ -z "$1" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
  sed -n '2,7p' "$0" | sed 's/^# \{0,1\}//'
  [ -z "$1" ] && exit 1 || exit 0
fi

python3 - "$1" "${2:-./src}" <<'PYTHON'
import base64, json, lzma, pathlib, re, sys

bundle, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
if not bundle.is_file():
    sys.exit(f"Error: bundle file not found: {bundle}")
m = re.search(r"VANILLA-ARTIFACT-SOURCE-MAP-V1 (\{.*?\}) -->", bundle.read_text(encoding="utf-8"), re.S)
if not m:
    sys.exit(f"Error: no VANILLA-ARTIFACT-SOURCE-MAP-V1 metadata in {bundle}")

for name, encoded in json.loads(m.group(1)).items():
    path = (out / name).resolve()
    if out.resolve() not in path.parents:
        sys.exit(f"Error: refusing to write outside {out}: {name}")
    data = base64.b64decode(encoded)
    try:
        data = lzma.decompress(data)
    except lzma.LZMAError:
        pass  # bundles before LZMA compression stored raw base64
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    print(f"  {name}")
print(f"Extracted to {out}")
PYTHON

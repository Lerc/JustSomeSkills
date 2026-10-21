#!/bin/bash
# Check whether this environment can run vanilla-artifact-builder.
#
# Usage: check-environment.sh [--quick]
#
#   --quick  Check tools only; skip the init -> bundle -> unbundle round trip
#            (the round trip installs npm packages into a temporary directory).
#
# Prints one PASS/FAIL line per check. Exit status 0 means the skill is usable.
# Honours $VANILLA_ARTIFACT_OUTPUT_DIR: it must be writable when set.

SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
FAILED=0
pass() { echo "PASS  $1"; }
fail() { echo "FAIL  $1"; echo "      -> $2"; FAILED=1; }

for tool in node npm npx python3; do
  if command -v "$tool" >/dev/null 2>&1; then
    pass "$tool found ($("$tool" --version 2>&1 | head -1))"
  else
    fail "$tool not found" "install Node.js (for node/npm/npx) or Python 3"
  fi
done

if python3 -c 'import lzma' 2>/dev/null; then
  pass "python3 lzma module"
else
  fail "python3 lzma module missing" "use a Python build with lzma support"
fi

if [ -n "$VANILLA_ARTIFACT_OUTPUT_DIR" ]; then
  if mkdir -p "$VANILLA_ARTIFACT_OUTPUT_DIR" 2>/dev/null && [ -w "$VANILLA_ARTIFACT_OUTPUT_DIR" ]; then
    pass "output dir writable: $VANILLA_ARTIFACT_OUTPUT_DIR"
  else
    fail "output dir not writable: $VANILLA_ARTIFACT_OUTPUT_DIR" "set VANILLA_ARTIFACT_OUTPUT_DIR to a writable delivery directory"
  fi
else
  pass "VANILLA_ARTIFACT_OUTPUT_DIR unset (bundles will be written into the project directory)"
fi

if [ "$1" = "--quick" ] || [ "$FAILED" -ne 0 ]; then
  [ "$FAILED" -ne 0 ] && echo "Skipping round trip: fix the failures above first."
  exit $FAILED
fi

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
PROJECT="$WORK/probe"
LOG="$WORK/log.txt"

"$SCRIPTS/init-vanilla-artifact.sh" "$PROJECT" >"$LOG" 2>&1
# A 1x1 PNG proves images are inlined and recoverable.
python3 -c 'import base64,sys; open(sys.argv[1],"wb").write(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="))' "$PROJECT/src/images/dot.png"
sed -i.bak 's|</body>|<img src="./images/dot.png" alt=""></body>|' "$PROJECT/src/index.html" && rm "$PROJECT/src/index.html.bak"

if VANILLA_ARTIFACT_OUTPUT_DIR="$WORK/out" "$SCRIPTS/bundle-vanilla-artifact.sh" "$PROJECT" >>"$LOG" 2>&1; then
  pass "bundle built (npm install + Parcel + inline)"
else
  fail "bundle failed" "npm registry access is required on first run; log tail:"
  tail -15 "$LOG" | sed 's/^/        /'
  exit 1
fi

BUNDLE="$WORK/out/probe.html"
LOCAL_REFS="$(python3 -c '
import re, sys
page = open(sys.argv[1], encoding="utf-8").read().split("VANILLA-ARTIFACT-SOURCE-MAP-V1")[0]
refs = re.findall(r"""(?:\b(?:src|href)\s*=\s*["'"'"']?|url\(\s*["'"'"']?)([^"'"'"'\s>)]+)""", page)
print(" ".join(r for r in refs if not re.match(r"(data:|https?:|//|#)", r)))
' "$BUNDLE")"
if [ -n "$LOCAL_REFS" ]; then
  fail "bundle still references external files" "inline_html.py left local references: $LOCAL_REFS"
else
  pass "bundle is self-contained ($(du -h "$BUNDLE" | cut -f1))"
fi

if "$SCRIPTS/unbundle-vanilla-artifact.sh" "$BUNDLE" "$WORK/restored" >>"$LOG" 2>&1 \
   && diff -r "$PROJECT/src" "$WORK/restored" >>"$LOG" 2>&1; then
  pass "unbundle restores src/ byte-for-byte"
else
  fail "unbundle round trip differs" "log tail:"
  tail -15 "$LOG" | sed 's/^/        /'
fi

[ "$FAILED" -eq 0 ] && echo "Environment can use vanilla-artifact-builder."
exit $FAILED

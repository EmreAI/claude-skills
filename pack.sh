#!/bin/sh
# Rebuilds dist/<skill>.zip for every skill folder (README.md stays out of the ZIP).
set -e
cd "$(dirname "$0")"
mkdir -p dist
for d in */; do
  d=${d%/}
  [ -f "$d/SKILL.md" ] || continue
  rm -f "dist/$d.zip"
  zip -rq -X "dist/$d.zip" "$d" -x '*.DS_Store' "$d/README.md"
  echo "dist/$d.zip"
done

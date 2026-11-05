#!/usr/bin/env bash
# Fetch the CC0 MakeHuman data files Version 2 needs (base mesh, targets, skeleton, weights).
# Usage: v2/tools/fetch_makehuman_data.sh [DEST]   then   export MH_DATA=DEST/makehuman/data
set -euo pipefail
DEST="${1:-$HOME/mh}"
if [ ! -d "$DEST/.git" ]; then
  git clone --depth 1 --filter=blob:none --sparse https://github.com/makehumancommunity/makehuman.git "$DEST"
fi
cd "$DEST"
git sparse-checkout set makehuman/data/3dobjs makehuman/data/rigs \
  makehuman/data/targets/macrodetails makehuman/data/targets/head makehuman/data/targets/eyes
echo "export MH_DATA=$DEST/makehuman/data"

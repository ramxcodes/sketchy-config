#!/usr/bin/env bash
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
set -euo pipefail
# Prefer a window on the home workspace, then any existing window of this app.
# Usage: summon.sh <AeroSpace app name> <workspace> [open -a name]
if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo 'Usage: summon.sh <app name> <workspace> [launch name]' >&2
  exit 1
fi
app="$1"
ws="$2"
open_name="${3:-$1}"

id="$(aerospace list-windows --all --format '%{window-id}|%{workspace}|%{app-name}' \
  | perl -CS -pe 's/[\x{200e}\x{200f}\x{202a}-\x{202e}]//g' \
  | awk -F'|' -v w="$ws" -v a="$app" '
      $3 == a && first == "" { first = $1 }
      $3 == a && $2 == w && home == "" { home = $1 }
      END { if (home != "") print home; else if (first != "") print first }
    ')"

if [[ -n "$id" ]]; then
  aerospace focus --window-id "$id"
else
  aerospace workspace "$ws"
  open -a "$open_name"
fi
# A bar refresh is optional once the focus or launch operation has succeeded.
if ! sketchybar --trigger bar_refresh; then
  echo 'App action completed, but SketchyBar could not refresh.' >&2
fi

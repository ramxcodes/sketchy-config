#!/usr/bin/env bash
# Copy configuration only. Services and system preferences are managed separately.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SB="$HOME/.config/sketchybar"

if [[ "$(uname -s)" != Darwin ]]; then
  echo "This configuration requires macOS. No files were changed." >&2
  exit 1
fi
for tool in aerospace sketchybar perl; do
  if ! command -v "$tool" >/dev/null; then
    echo "Missing $tool. Follow the dependency steps in README.md first." >&2
    exit 1
  fi
done
# Check managed files and their parent directories before creating a backup.
for target in "$HOME/.config" "$HOME/.aerospace.toml" "$SB" "$SB/plugins" \
  "$SB/sketchybarrc" "$SB/apps.conf" "$SB/colors.sh" "$SB/plugins/"*.sh; do
  if [[ -L "$target" ]]; then
    echo "A target is a symbolic link: $target. Use the manual install steps in README.md." >&2
    exit 1
  fi
done

mkdir -p "$HOME/.config"
backup="$(mktemp -d "$HOME/.config/sketchy-config-backup.XXXXXXXX")"
if [[ -e "$HOME/.aerospace.toml" ]]; then
  cp -p "$HOME/.aerospace.toml" "$backup/aerospace.toml"
fi
if [[ -e "$SB" ]]; then
  cp -Rp "$SB" "$backup/sketchybar"
fi

mkdir -p "$SB/plugins"
install -m 0644 "$ROOT/config/aerospace.toml" "$HOME/.aerospace.toml"
install -m 0755 "$ROOT/config/sketchybar/sketchybarrc" "$SB/sketchybarrc"
install -m 0644 "$ROOT/config/sketchybar/apps.conf" "$ROOT/config/sketchybar/colors.sh" "$SB/"
install -m 0755 "$ROOT/config/sketchybar/plugins/"*.sh "$SB/plugins/"

printf 'Configuration copied. Backup: %s\n' "$backup"
printf '%s\n' 'Next, follow the start and permissions steps in README.md.'

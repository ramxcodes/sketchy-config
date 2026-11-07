#!/usr/bin/env bash
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
DIR="${CONFIG_DIR:-$HOME/.config/sketchybar}"
source "$DIR/colors.sh"

line="$(pmset -g batt | awk '/InternalBattery/{print}')"
[[ -z "$line" ]] && { sketchybar --set "$NAME" drawing=off; exit 0; }

pct="$(sed -n 's/.*\t\([0-9][0-9]*\)%.*/\1/p' <<<"$line")"
[[ -z "$pct" ]] && { sketchybar --set "$NAME" drawing=off; exit 0; }

# Only the active charge state — not "discharging" (substring trap) or "charged".
charging=false
[[ "$line" == *"; charging;"* || "$line" == *"; finishing charge;"* ]] && charging=true

if $charging; then
  cp=F0084
  color="$CHARGE"
else
  levels=(F008E F007A F007B F007C F007D F007E F007F F0080 F0081 F0082 F0079)
  cp="${levels[$((pct / 10))]}"
  color="$FG_WHITE"
fi

sketchybar --set "$NAME" \
  icon="$(perl -CS -e "print chr(0x$cp)")" \
  icon.color="$color" \
  label="${pct}%" label.color="$color" label.drawing=on drawing=on

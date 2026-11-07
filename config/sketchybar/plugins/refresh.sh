#!/usr/bin/env bash
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
# Rebuild workspace pills for main and secondary monitors.
DIR="${CONFIG_DIR:-$HOME/.config/sketchybar}"
LOCK="${HOME}/.cache/sketchy-config/refresh.lock"
mkdir -p "$(dirname "$LOCK")"

# Skip if another refresh is already running.
if ! mkdir "$LOCK" 2>/dev/null; then
  exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null' EXIT

source "$DIR/colors.sh"
source "$DIR/plugins/icon_map.sh"

TMP=$(mktemp -d) || exit 1
trap 'rm -rf "$TMP"; rmdir "$LOCK" 2>/dev/null' EXIT

# Stop on a failed AeroSpace query so a stopped service cannot clear the bar.
aerospace list-workspaces --focused >"$TMP/ws" || exit 1
aerospace list-monitors --focused --format '%{monitor-is-main}' >"$TMP/fm" || exit 1
aerospace list-monitors --format '%{monitor-id}|%{monitor-is-main}|%{monitor-appkit-nsscreen-screens-id}' >"$TMP/mons" || exit 1
aerospace list-windows --all --format '%{monitor-id}|%{workspace}|%{app-name}' >"$TMP/wins" || exit 1

focused_ws=$(cat "$TMP/ws")
focused_is_main=$(cat "$TMP/fm")
perl -CS -pe 's/[\x{200e}\x{200f}\x{202a}-\x{202e}]//g' <"$TMP/wins" >"$TMP/wins.clean"

main_mid=; ext_mid=; main_ns=1; ext_ns=2; n=0
while IFS='|' read -r mid is_main ns; do
  [[ -z "$mid" ]] && continue
  n=$((n + 1))
  if [[ "$is_main" == true ]]; then
    main_mid=$mid; main_ns=${ns:-1}
  else
    ext_mid=$mid; ext_ns=${ns:-2}
  fi
done <"$TMP/mons"

: >"$TMP/main"; : >"$TMP/ext"
awk -F'|' -v main="$main_mid" -v ext="$ext_mid" -v md="$TMP/main" -v ed="$TMP/ext" '
  $3 == "" { next }
  seen[$1, $2, $3]++ { next }
  $1 == main { print $2 "|" $3 >> md; next }
  $1 == ext  { print $2 "|" $3 >> ed }
' "$TMP/wins.clean"

apps_for() {
  apps=()
  while IFS='|' read -r w a; do
    [[ "$w" == "$1" && -n "$a" ]] && apps+=("$a")
  done <"$2"
}

paint_side() {
  local suffix="$1" mid="$2" focused_side="$3" disp="$4" side_file="$5"
  local key focus_label idle_label idle_font label font bg fg lfg pad draw

  if [[ -z "$mid" ]]; then
    while IFS='|' read -r key _; do
      [[ -z "$key" || "$key" == \#* ]] && continue
      args+=(--set "sp.$key.$suffix" drawing=off)
    done <"$DIR/apps.conf"
    return
  fi

  while IFS='|' read -r key _; do
    [[ -z "$key" || "$key" == \#* ]] && continue
    apps_for "$key" "$side_file"
    idle_font="sketchybar-app-font:Regular:15.0"

    if [[ ${#apps[@]} -eq 0 ]]; then
      if [[ "$focused_side" == true && "$key" == "$focused_ws" ]]; then
        args+=(--set "sp.$key.$suffix" position=left drawing=on display="$disp" \
          background.color="$BG_ON" icon.color="$ACCENT" icon.padding_right=11 \
          label.drawing=off)
      else
        args+=(--set "sp.$key.$suffix" drawing=off)
      fi
      continue
    fi

    focus_label="$(printf '%s, ' "${apps[@]}")"
    focus_label="${focus_label%, }"

    idle_label=""
    for a in "${apps[@]}"; do
      __icon_map "$a"
      idle_label+="${icon_result} "
    done
    idle_label="${idle_label% }"

    if [[ "$focused_side" == true && "$key" == "$focused_ws" ]]; then
      label="$focus_label"; font="Helvetica Neue:Medium:12.0"
      bg="$BG_ON"; fg="$ACCENT"; lfg="$FG_ON"
    else
      label="$idle_label"; font="$idle_font"
      bg="$BG_OFF"; fg="$FG_OFF"; lfg="$FG_OFF"
    fi
    if [[ -n "$label" ]]; then pad=0; draw=on; else pad=11; draw=off; fi

    args+=(--set "sp.$key.$suffix" position=left drawing=on display="$disp" \
      background.color="$bg" icon.color="$fg" icon.padding_right="$pad" \
      label="$label" label.color="$lfg" label.font="$font" label.drawing="$draw")
  done <"$DIR/apps.conf"
}

args=()
main_focused=false; ext_focused=false
[[ "$focused_is_main" == true ]] && main_focused=true || ext_focused=true
paint_side m "$main_mid" "$main_focused" "$main_ns" "$TMP/main"
if [[ "$n" -ge 2 && -n "$ext_mid" ]]; then
  paint_side e "$ext_mid" "$ext_focused" "$ext_ns" "$TMP/ext"
else
  paint_side e "" false "$main_ns" "$TMP/ext"
fi

if [[ "$n" -lt 2 ]]; then
  args+=(--set mon.1 drawing=on icon.color="$ACCENT" background.color="$BG_ON" \
    --set mon.2 drawing=off)
elif [[ "$focused_is_main" == true ]]; then
  args+=(--set mon.1 drawing=on icon.color="$ACCENT" background.color="$BG_ON" \
    --set mon.2 drawing=on icon.color="$FG_OFF" background.color="$BG_OFF")
else
  args+=(--set mon.1 drawing=on icon.color="$FG_OFF" background.color="$BG_OFF" \
    --set mon.2 drawing=on icon.color="$ACCENT" background.color="$BG_ON")
fi

sketchybar "${args[@]}"

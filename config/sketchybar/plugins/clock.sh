#!/usr/bin/env bash
# 12-hour clock, e.g. "3:45 PM"
time="$(date +"%l:%M %p" | sed 's/^ //')"
sketchybar --set "$NAME" label="$time" drawing=on

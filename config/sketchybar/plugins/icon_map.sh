#!/usr/bin/env bash
# App name to sketchybar-app-font glyph. Unknown apps use a generic icon.
__icon_map() {
  case "$1" in
    "Finder") icon_result=":finder:" ;;
    "Ghostty") icon_result=":ghostty:" ;;
    "Safari") icon_result=":safari:" ;;
    "Spotify") icon_result=":spotify:" ;;
    "Code" | "Visual Studio Code") icon_result=":code:" ;;
    "WhatsApp") icon_result=":whats_app:" ;;
    *) icon_result=":default:" ;;
  esac
}

#!/usr/bin/env bash
# =============================================================================
# colors.sh — the whole palette. Change a value here and everything using it
# updates on the next `sketchybar --reload`.
#
# FORMAT: 0xAARRGGBB  (AA = alpha/opacity, then red green blue; all hex).
#   e.g. 0xff111111 = fully opaque near-black.  0x80... = 50% transparent.
# =============================================================================
BG_OFF=0xff111111   # idle pill background
BG_ON=0xff1c1c1c    # focused pill background
FG_OFF=0xff3a3a3a   # idle letter + app glyphs
FG_ON=0xffc9c9c9    # focused app names + clock
FG_WHITE=0xffffffff # battery when not charging
CHARGE=0xff34c759   # battery icon + % when charging
ACCENT=0xff0a84ff   # apple mark + focused letter (system blue)

#!/usr/bin/env bash
# Open the real macOS Apple menu of the frontmost application.
# macOS requires Accessibility permission for SketchyBar to do this.
/usr/bin/osascript <<'APPLESCRIPT'
tell application "System Events"
  set frontProcess to first application process whose frontmost is true
  tell frontProcess to click menu bar item 1 of menu bar 1
end tell
APPLESCRIPT

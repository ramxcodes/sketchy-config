# Usage and recovery

The [README](../README.md#shortcuts) lists all shortcuts and monitor behavior.

## Missing or incorrect app icons

Install `font-sketchybar-app-font` and `font-hack-nerd-font`, then restart SketchyBar:

```bash
brew services restart sketchybar
```

Check the app name with `aerospace list-windows --all --format '%{app-name}'`. Add its glyph in `plugins/icon_map.sh` if needed. An unknown app uses a generic icon.

## A shortcut does not open an app

Test its launch name directly, for example:

```bash
open -a 'Visual Studio Code'
```

Install the app or update the binding to use your app's name. If the app is already open but the shortcut does not find its window, compare its AeroSpace app name with the first argument to `summon.sh`.

## The bar is missing or stale

```bash
brew services list
aerospace list-monitors
sketchybar --reload
```

AeroSpace must be running. The bar refreshes on workspace changes, display changes, wake, and every ten seconds. A failed AeroSpace query stops that refresh instead of clearing the bar. Script errors appear in SketchyBar's service logs, usually under the Homebrew log directory.

If a script was forcibly killed during refresh, it can leave a lock directory. Stop SketchyBar before removing that lock, then restart it:

```bash
brew services stop sketchybar
rmdir ~/.cache/sketchy-config/refresh.lock
brew services start sketchybar
```

Only remove the lock when no refresh process is running. `rmdir` reports an error if the lock does not exist; continue with the start command in that case.

## Monitor buttons are wrong

Confirm the main display in System Settings. Run:

```bash
aerospace list-monitors --format '%{monitor-id}|%{monitor-is-main}|%{monitor-appkit-nsscreen-screens-id}'
```

The bar maps AeroSpace monitor IDs to SketchyBar display IDs. It supports one main and one secondary display. After connecting or disconnecting a screen, allow a refresh or run `sketchybar --reload`. Three or more displays need the changes described in the README.

## Restore your previous configuration

Stop the bar first:

```bash
brew services stop sketchybar
```

Use the backup path printed by the installer. Replace `XXXXXXXX` below with your backup's suffix:

```bash
backup="$HOME/.config/sketchy-config-backup.XXXXXXXX"
ls "$backup"
```

Move the installed `~/.config/sketchybar` folder out of the way. If the backup contains `sketchybar`, copy it back to `~/.config/sketchybar`. If the backup contains `aerospace.toml`, copy it back to `~/.aerospace.toml`. If a backup file is absent, that configuration did not exist before installation, so remove the installed copy instead.

Run `aerospace reload-config` after restoring an AeroSpace config. If you removed it, quit AeroSpace and restore your own setup before restarting. Restart your previous bar service only after restoring its config.

The installer does not change system preferences. If you changed menu bar auto-hide manually, restore your preferred setting in System Settings. To stop AeroSpace from starting at login, set `start-at-login = false` in the config you keep.

# sketchy-config

A macOS window and menu bar setup built with [AeroSpace](https://github.com/nikitabobko/AeroSpace) and [SketchyBar](https://github.com/FelixKratz/SketchyBar).

Use Option plus an app's letter to focus its window, or launch it if it has no window. Move windows with Control + Option + Command and the arrow keys. Switch monitors with Control + Option and the arrow keys.

The bar shows workspace pills, app icons, a clock, battery status, and monitor buttons. Empty workspaces hide until selected. The defaults support one or two monitors, using monitor roles instead of a device name. No personal accounts, paid utilities, window border tool, or custom background service are needed.

## Requirements

- macOS 14 or later, on Apple Silicon or Intel.
- [Homebrew](https://brew.sh).
- AeroSpace **0.21.3-Beta or later**. This config uses `config-version = 2`.
- SketchyBar, `sketchybar-app-font`, and Hack Nerd Font.
- Ghostty, Spotify, Visual Studio Code, and WhatsApp are optional. Their shortcuts need the matching app installed. The installer does not install these apps.

This repository cannot provide tiling or a menu bar on Linux or Windows.

## Install

### 1. Install dependencies

```bash
brew tap nikitabobko/tap
brew tap FelixKratz/formulae
brew install --cask nikitabobko/tap/aerospace
brew install sketchybar
brew install --cask font-sketchybar-app-font font-hack-nerd-font
```

The bar uses the system Helvetica Neue font for text. Both standard Homebrew binary locations are supported. If you use a custom Homebrew prefix, add its `bin` directory to the PATH in `sketchybarrc` and the plugins.

### 2. Copy the configuration

```bash
git clone https://github.com/ramxcodes/sketchy-config.git
cd sketchy-config
./install.sh
```

The installer checks dependencies, backs up existing files under `~/.config/sketchy-config-backup.XXXXXXXX`, and copies:

| Repository file | Installed location |
| --- | --- |
| `config/aerospace.toml` | `~/.aerospace.toml` |
| `config/sketchybar/` | `~/.config/sketchybar/` |

It replaces matching files and leaves unrelated files in the SketchyBar folder. It does not start services, install packages, or change macOS preferences. It refuses to overwrite symbolic-link targets. Keep a copy of the printed backup path.

For a manual install, first back up your existing files. Copy `config/aerospace.toml` to `~/.aerospace.toml` and the contents of `config/sketchybar/` to `~/.config/sketchybar/`. Make `sketchybarrc` and `plugins/*.sh` executable. If you use symbolic links, update the files in your own dotfiles repository instead.

AeroSpace can also read `~/.config/aerospace/aerospace.toml`. If you already have that file, move it to your backup before using this setup, so AeroSpace has only one configuration to choose from.

### 3. Start the tools

```bash
open -a AeroSpace
brew services start sketchybar
```

In **System Settings > Privacy & Security > Accessibility**, allow AeroSpace. Allow SketchyBar if you want the Apple icon to open the native Apple menu. This setup does not need Screen Recording access.

If both tools were already running:

```bash
aerospace reload-config
sketchybar --reload
```

AeroSpace starts at login through `start-at-login = true`. Homebrew manages SketchyBar's background service. Use one SketchyBar service only. If you previously installed a custom LaunchAgent, disable that service before starting the Homebrew service.

### 4. Set your menu bar preference

For the intended top bar layout, set **System Settings > Control Center > Automatically hide and show the menu bar** to **Always**. The setting's location can differ by macOS version. Move the pointer to the top edge to reveal the native menu bar.

The top window gap is a constant `46` points, rather than a value tied to a particular Mac. Adjust `gaps.outer.top` in `config/aerospace.toml` if your notch or menu bar settings need more or less space.

## Shortcuts

`Option` is written as `alt` in AeroSpace's config. App shortcuts prefer a window on the app's home workspace, then any existing window on another workspace or monitor. If there is no window, the shortcut selects the home workspace and opens the app.

| Shortcut | App | Home workspace |
| --- | --- | --- |
| Option + G | Ghostty | G |
| Option + M | Spotify | M |
| Option + V | Visual Studio Code | V |
| Option + W | WhatsApp | W |

New app windows stay on the workspace where you open them. There are no forced app placement rules. Option + Shift + G/M/V/W moves the focused window to the matching workspace.

| Shortcut | Action |
| --- | --- |
| Option + 1 through 6 | Select a scratch workspace |
| Option + Shift + 1 through 6 | Move the focused window to a scratch workspace |
| Option + Tab | Focus the next window on this workspace |
| Option + Shift + Tab | Focus the previous window |
| Option + F | Toggle fullscreen |
| Control + Option + Command + arrow | Rearrange the focused window |
| Control + Option + arrow | Focus a monitor in that direction |
| Control + Option + 1/2 | Focus the main/secondary monitor |
| Control + Option + Shift + arrow | Move the focused window to a monitor and follow it |
| Control + Option + Shift + 1/2 | Move the focused window to the main/secondary monitor and follow it |
| Control + Option + Shift + Tab | Move the focused workspace to the next monitor |

Option + arrow remains available for macOS text navigation. Command + H and Command + Option + H are disabled to avoid hiding managed windows. Delete their empty bindings to restore normal macOS behavior.

## Monitors and workspaces

Choose your main display in **System Settings > Displays**. Directional shortcuts follow the display arrangement there, so the setup works with screens beside or above one another.

| Workspaces | Monitor |
| --- | --- |
| 1, 2, 3 | Main |
| 4, 5, 6 | Secondary, or main when only one display is connected |
| G, M, V, W | Free to move between monitors |

The `1` and `2` buttons beside the clock focus the main and secondary monitors. The active monitor button is highlighted. The second set of workspace pills hides when there is one monitor. Shared items use SketchyBar's default display association to appear once on each connected display. The battery item hides on computers with no battery.

To move an app alone to another screen, focus it and press Control + Option + Shift + Tab. To tile several apps together, move their windows to the same workspace. Moving a window to a monitor joins the workspace already visible on that monitor.

Scratch workspaces have fixed monitor assignments. The whole-workspace move shortcut cannot move them. Use it on letter workspaces instead. Secondary-monitor shortcuts require a second monitor.

The included bar has two display slots. For three or more monitors, extend the display loops and monitor mapping in `sketchybarrc` and `plugins/refresh.sh`, and replace `secondary` assignments with monitor numbers or name patterns. See [AeroSpace monitor assignments](https://nikitabobko.github.io/AeroSpace/guide#assign-workspaces-to-monitors).

## Customize

- [Add or replace an app](docs/adding-apps.md).
- Change pill order in `config/sketchybar/apps.conf`.
- Change colors in `config/sketchybar/colors.sh`.
- Change gaps, keys, and monitor assignments in `config/aerospace.toml`.
- Change bar height and fonts in `config/sketchybar/sketchybarrc`.

Edit the repository copies, run `./install.sh`, then reload both tools. Changes made only to installed files are overwritten on the next install.

## Good practices

Back up before trying a new setup. Keep app names and workspace keys consistent between `aerospace.toml` and `apps.conf`. Change one binding at a time and reload to check it. Do not disable macOS security protections for these tools.

Use `aerospace list-windows --all --format '%{app-name}'` to find the actual app name. It may differ from the name in `/Applications`. VS Code, for example, normally reports `Code` but launches as `Visual Studio Code`.

Keep personal app rules and machine-specific monitor names in your own fork. Before sharing changes, check for usernames, home paths, credentials, and files generated by your computer. Review tool upgrades before applying them, especially AeroSpace beta releases.

## Troubleshooting and removal

See [usage and recovery](docs/usage.md) for missing icons, stale pills, service problems, and restoring a backup.

## Checks

Use Python 3.11 or later for the local checks.

```bash
python3 -m unittest discover -s tests -v
```

These checks run the installer and plugins in temporary folders with simulated command output. They cover backups, failure cases, app selection, and one/two-monitor bar updates. They do not prove macOS permissions, rendering, or physical keyboard behavior. Those need a Mac. Shell syntax and TOML structure can be checked on Linux too.

## Credits and license

Configuration by [Ram](https://github.com/ramxcodes), adapted from his personal setup. Built on AeroSpace and SketchyBar. App glyphs come from [sketchybar-app-font](https://github.com/kvndrsslr/sketchybar-app-font); battery and Apple glyphs use [Hack Nerd Font](https://www.nerdfonts.com/). These dependencies keep their own licenses.

This configuration is available under the [MIT license](LICENSE).

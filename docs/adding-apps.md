# Add or replace an app

Pick an unused letter. This example gives Slack workspace `S`.

## Find the names

Open the app, then run:

```bash
aerospace list-windows --all --format '%{app-name}|%{app-bundle-id}'
osascript -e 'id of app "Slack"'
```

Use the exact AeroSpace app name for window matching. Use the application name accepted by `open -a` for launching. They can differ.

## Add the workspace and shortcuts

Add `"S"` to `persistent-workspaces` in `config/aerospace.toml`. Inside `[mode.main.binding]`, add:

```toml
alt-s = 'exec-and-forget ~/.config/sketchybar/plugins/summon.sh Slack S Slack'
alt-shift-s = 'move-node-to-workspace S'
```

For names with spaces, quote each argument separately. VS Code's existing binding shows how to use a different launch name.

## Add the bar item

Append this line to `config/sketchybar/apps.conf`:

```text
S|Slack|Slack
```

The fields are workspace key, AeroSpace app name, and launch name for `open -a`. Leave the launch name empty to use the AeroSpace name. For VS Code, use `V|Code|Visual Studio Code`. Reorder lines to change bar order.

In `config/sketchybar/plugins/icon_map.sh`, add a case before the default case:

```bash
"Slack") icon_result=":slack:" ;;
```

Use a glyph supported by sketchybar-app-font. Apps without a mapping still show a generic icon.

## Apply

```bash
./install.sh
aerospace reload-config
sketchybar --reload
```

Test the shortcut with the app closed, with a window on its home workspace, and with a window on another workspace. Extra windows stay where you open them.

To remove an app, delete its workspace from `persistent-workspaces`, its two bindings, its `apps.conf` line, and any unused icon mapping. To replace an app, update those same entries. Do not add an automatic window placement rule unless you want every new window to move to that workspace.

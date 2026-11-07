"""Run the actual shell scripts against isolated command-line fixtures."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
FAKE_TOOL = '''#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys
name = Path(sys.argv[0]).name
args = sys.argv[1:]
with open(os.environ["CALL_LOG"], "a") as log:
    log.write(json.dumps([name, *args]) + "\\n")
if os.environ.get("FAIL_TOOL") == name:
    print("fixture: command failed", file=sys.stderr)
    sys.exit(1)
if name == "uname":
    print(os.environ.get("PLATFORM", "Darwin"))
elif name == "aerospace":
    if args[0] == "list-windows":
        print(os.environ.get("WINDOWS", ""))
    elif args[0] == "list-workspaces":
        print(os.environ.get("WORKSPACE", "G"))
    elif args[0] == "list-monitors":
        if "--focused" in args:
            print(os.environ.get("MAIN_FOCUSED", "true"))
        else:
            print(os.environ.get("MONITORS", "1|true|1"))
elif name == "pmset":
    print(os.environ.get("BATTERY", ""))
'''


class Scripts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="sketchy-config-test-")
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.home = self.folder / "home"
        self.home.mkdir()
        self.bin = self.folder / "bin"
        self.bin.mkdir()
        self.log = self.folder / "calls.jsonl"
        self.env = {
            **os.environ,
            "HOME": str(self.home),
            "PATH": f"{self.bin}:{os.environ['PATH']}",
            "CALL_LOG": str(self.log),
            "CONFIG_DIR": str(ROOT / "config/sketchybar"),
        }
        for name in ("uname", "aerospace", "sketchybar", "open", "pmset"):
            tool = self.bin / name
            tool.write_text(FAKE_TOOL)
            tool.chmod(0o755)

    def run_script(self, script, *args, **env):
        return subprocess.run(
            ["bash", str(ROOT / script), *args],
            env={**self.env, **env}, capture_output=True, text=True,
        )

    def calls(self, name):
        if not self.log.exists():
            return []
        return [call[1:] for line in self.log.read_text().splitlines()
                if (call := json.loads(line))[0] == name]

    def refresh(self, **env):
        result = self.run_script("config/sketchybar/plugins/refresh.sh", **env)
        self.assertEqual(result.returncode, 0, result.stderr)
        args = [arg for call in self.calls("sketchybar") for arg in call]
        items = {}
        for value in args:
            if value == "--set":
                current = None
            elif current is None:
                current = value
                items.setdefault(current, {})
            else:
                key, setting = value.split("=", 1)
                items[current][key] = setting
        return items

    def test_installer_backs_up_and_reinstalls(self):
        target = self.home / ".config/sketchybar"
        target.mkdir(parents=True)
        (target / "sketchybarrc").write_text("previous bar")
        old_aero = self.home / ".aerospace.toml"
        old_aero.write_text("previous aerospace")
        for _ in range(2):
            result = self.run_script("install.sh")
            self.assertEqual(result.returncode, 0, result.stderr)
        backups = sorted((self.home / ".config").glob("sketchy-config-backup.*"))
        self.assertEqual(len(backups), 2)
        self.assertTrue(any((b / "aerospace.toml").read_text() == "previous aerospace"
                            for b in backups))
        self.assertTrue(any((b / "sketchybar/sketchybarrc").read_text() == "previous bar"
                            for b in backups))
        self.assertEqual(old_aero.read_bytes(), (ROOT / "config/aerospace.toml").read_bytes())
        self.assertTrue(os.access(target / "plugins/summon.sh", os.X_OK))
        self.assertEqual(self.calls("sketchybar"), [])
        self.assertEqual(self.calls("aerospace"), [])

    def test_installer_rejects_linux_without_writes(self):
        result = self.run_script("install.sh", PLATFORM="Linux")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_installer_rejects_missing_tool_without_writes(self):
        (self.bin / "aerospace").unlink()
        result = self.run_script("install.sh")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing aerospace", result.stderr)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_installer_refuses_symlink(self):
        original = self.folder / "original"
        original.write_text("keep me")
        (self.home / ".aerospace.toml").symlink_to(original)
        result = self.run_script("install.sh")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(original.read_text(), "keep me")
        self.assertFalse((self.home / ".config").exists())

    def test_installer_refuses_linked_plugin_directory_and_files(self):
        target = self.home / ".config/sketchybar"
        target.mkdir(parents=True)
        outside = self.folder / "external-plugins"
        outside.mkdir()
        original = outside / "summon.sh"
        original.write_text("keep this plugin")
        (target / "plugins").symlink_to(outside)
        result = self.run_script("install.sh")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(original.read_text(), "keep this plugin")
        self.assertEqual(list(outside.iterdir()), [original])
        self.assertFalse((self.home / ".aerospace.toml").exists())
        self.assertEqual(list((self.home / ".config").glob("sketchy-config-backup.*")), [])
        (target / "plugins").unlink()
        (target / "plugins").mkdir()
        for relative in ("plugins/summon.sh", "sketchybarrc", "apps.conf", "colors.sh"):
            with self.subTest(relative=relative):
                link = target / relative
                link.symlink_to(original)
                result = self.run_script("install.sh")
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(original.read_text(), "keep this plugin")
                self.assertFalse((self.home / ".aerospace.toml").exists())
                link.unlink()

    def test_summon_prefers_home_window(self):
        result = self.run_script("config/sketchybar/plugins/summon.sh", "Code", "V",
                                 "Visual Studio Code", WINDOWS="10|3|Code\n20|V|Code")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(["focus", "--window-id", "20"], self.calls("aerospace"))
        self.assertEqual(self.calls("open"), [])

    def test_summon_finds_window_on_another_workspace(self):
        result = self.run_script("config/sketchybar/plugins/summon.sh", "Code", "V",
                                 WINDOWS="10|3|Code\n20|G|Ghostty")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(["focus", "--window-id", "10"], self.calls("aerospace"))
        self.assertEqual(self.calls("open"), [])

    def test_summon_launches_with_separate_name(self):
        result = self.run_script("config/sketchybar/plugins/summon.sh", "Code", "V",
                                 "Visual Studio Code")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(["workspace", "V"], self.calls("aerospace"))
        self.assertEqual(self.calls("open"), [["-a", "Visual Studio Code"]])

    def test_summon_does_not_launch_after_query_failure(self):
        result = self.run_script("config/sketchybar/plugins/summon.sh", "Code", "V",
                                 FAIL_TOOL="aerospace")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.calls("open"), [])
        self.assertEqual(len(self.calls("aerospace")), 1)

    def test_summon_reports_launch_failure(self):
        result = self.run_script("config/sketchybar/plugins/summon.sh", "Code", "V",
                                 FAIL_TOOL="open")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.calls("sketchybar"), [])

    def test_bar_failure_does_not_fail_completed_app_action(self):
        result = self.run_script("config/sketchybar/plugins/summon.sh", "Code", "V",
                                 FAIL_TOOL="sketchybar")
        self.assertEqual(result.returncode, 0)
        self.assertIn("could not refresh", result.stderr)
        self.assertEqual(self.calls("open"), [["-a", "Code"]])

    def test_refresh_one_monitor_and_empty_focused_workspace(self):
        items = self.refresh(MONITORS="7|true|3", WORKSPACE="1", WINDOWS="7|G|Ghostty")
        self.assertEqual(items["sp.1.m"]["drawing"], "on")
        self.assertEqual(items["sp.G.m"]["display"], "3")
        self.assertEqual(items["sp.M.m"]["drawing"], "off")
        self.assertEqual(items["sp.G.e"]["drawing"], "off")
        self.assertEqual(items["mon.2"]["drawing"], "off")
        self.assertEqual(items["mon.2"]["drawing"], "off")

    def test_refresh_two_monitors_and_disconnect_reconnect(self):
        for _ in range(2):
            items = self.refresh(MONITORS="7|true|3\n9|false|6", MAIN_FOCUSED="false",
                                 WORKSPACE="V", WINDOWS="9|V|Code\n9|V|Code\n7|G|Ghostty")
            self.assertEqual(items["sp.V.e"]["display"], "6")
            self.assertEqual(items["sp.V.e"]["label"], "Code")
            self.assertEqual(items["sp.V.m"]["drawing"], "off")
            self.assertEqual(items["mon.2"]["background.color"], "0xff1c1c1c")
            self.assertEqual(items["mon.2"]["drawing"], "on")
            items = self.refresh()
            self.assertEqual(items["mon.2"]["drawing"], "off")
        self.assertFalse((self.home / ".cache/sketchy-config/refresh.lock").exists())

    def test_shared_items_do_not_duplicate_after_disconnect_and_periodic_update(self):
        result = self.run_script("config/sketchybar/sketchybarrc")
        self.assertEqual(result.returncode, 0, result.stderr)
        additions = [call[2] for call in self.calls("sketchybar")
                     if call[:2] == ["--add", "item"]]
        self.assertEqual(additions.count("clock"), 1)
        self.assertEqual(additions.count("battery"), 1)
        for name in ("clock", "battery", "apple"):
            call = next(call for call in self.calls("sketchybar")
                        if call[:3] == ["--add", "item", name])
            self.assertIn("display=0", call)
        self.log.write_text("")
        self.refresh(MONITORS="1|false|1\n2|true|2")
        self.refresh(MONITORS="1|true|1")
        for script, name in (("clock.sh", "clock"), ("battery.sh", "battery")):
            result = self.run_script(f"config/sketchybar/plugins/{script}", NAME=name,
                                     BATTERY=" -InternalBattery-0\t80%; discharging; 1:10 remaining")
            self.assertEqual(result.returncode, 0, result.stderr)
        for call in self.calls("sketchybar"):
            self.assertNotIn("clock.2", call)
            self.assertNotIn("battery.2", call)

    def test_refresh_does_not_override_battery_visibility(self):
        result = self.run_script("config/sketchybar/plugins/battery.sh", NAME="battery", BATTERY="")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("drawing=off", self.calls("sketchybar")[-1])
        self.log.write_text("")
        self.refresh(MONITORS="1|true|1\n2|false|2")
        for call in self.calls("sketchybar"):
            self.assertNotIn("battery", call)

    def test_vscode_bar_click_uses_launch_name(self):
        result = self.run_script("config/sketchybar/sketchybarrc")
        self.assertEqual(result.returncode, 0, result.stderr)
        clicks = []
        for call in self.calls("sketchybar"):
            if "sp.V.m" in call:
                clicks.extend(arg.removeprefix("click_script=") for arg in call
                              if arg.startswith("click_script="))
        self.assertEqual(len(clicks), 1)
        result = subprocess.run(["bash", "-c", clicks[0]], env=self.env,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.calls("open"), [["-a", "Visual Studio Code"]])

    def test_failed_refresh_preserves_bar_and_releases_lock(self):
        result = self.run_script("config/sketchybar/plugins/refresh.sh", FAIL_TOOL="aerospace")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.calls("sketchybar"), [])
        self.assertFalse((self.home / ".cache/sketchy-config/refresh.lock").exists())

    def test_battery_missing_charging_and_discharging(self):
        for line, drawing, color in (
            ("", "off", None),
            (" -InternalBattery-0\t80%; charging; 0:10 remaining", "on", "0xff34c759"),
            (" -InternalBattery-0\t80%; discharging; 1:10 remaining", "on", "0xffffffff"),
        ):
            result = self.run_script("config/sketchybar/plugins/battery.sh",
                                     NAME="battery", BATTERY=line)
            self.assertEqual(result.returncode, 0, result.stderr)
            args = self.calls("sketchybar")[-1]
            self.assertIn(f"drawing={drawing}", args)
            if color:
                self.assertIn(f"label.color={color}", args)


class Configuration(unittest.TestCase):
    def test_shell_syntax(self):
        files = [ROOT / "install.sh", ROOT / "config/sketchybar/sketchybarrc",
                 *(ROOT / "config/sketchybar/plugins").glob("*.sh")]
        for path in files:
            with self.subTest(path=path):
                result = subprocess.run(["bash", "-n", str(path)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_workspace_and_app_bindings_agree(self):
        config = tomllib.loads((ROOT / "config/aerospace.toml").read_text())
        keys = [line.split("|")[0] for line in
                (ROOT / "config/sketchybar/apps.conf").read_text().splitlines()
                if line and not line.startswith("#")]
        self.assertEqual(set(keys), set(config["persistent-workspaces"]))
        bindings = config["mode"]["main"]["binding"]
        for key in keys:
            self.assertIn(f"alt-{key.lower()}", bindings)
            self.assertEqual(bindings[f"alt-shift-{key.lower()}"], f"move-node-to-workspace {key}")
        self.assertIn('"Visual Studio Code"', bindings["alt-v"])
        for direction in ("left", "down", "up", "right"):
            self.assertEqual(bindings[f"ctrl-alt-cmd-{direction}"], f"move {direction}")
            self.assertIn(f"alt-ctrl-{direction}", bindings)
            self.assertIn(f"alt-ctrl-shift-{direction}", bindings)
        self.assertEqual(config["workspace-to-monitor-force-assignment"]["4"], ["secondary", "main"])

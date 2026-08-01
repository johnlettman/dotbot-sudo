import json
import subprocess
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

import pytest
from dotbot.context import Context

from sudo import Sudo


def get_context(base_directory: Path) -> Context:
    return Context(
        str(base_directory),
        Namespace(
            only=None,
            skip=None,
            plugins=[],
            plugin_dirs=[],
            disable_built_in_plugins=False,
            dry_run=False,
        ),
    )


class TestSudo:
    def test_can_handle(self) -> None:
        plugin = Sudo(None)
        assert plugin.can_handle("sudo")
        assert not plugin.can_handle("shell")

    def test_handle_rejects_non_list_tasks(self, tmp_path: Path) -> None:
        with pytest.raises(TypeError, match="expects a list"):
            Sudo(get_context(tmp_path)).handle("sudo", {})

    def test_handle_writes_defaults_and_inherits_terminal(self, tmp_path: Path) -> None:
        plugin = Sudo(get_context(tmp_path))
        plugin._context.set_defaults({"shell": {"stdin": True}})

        def inspect_config(args: list[str]) -> None:
            payload = json.loads(Path(args[-1]).read_text())
            assert payload == [
                {"defaults": {"shell": {"stdin": True}}},
                {"shell": ["true"]},
            ]

        with (
            patch.object(plugin, "_find_dotbot", return_value="/venv/bin/dotbot"),
            patch.object(plugin, "_collect_plugins", return_value=[]),
            patch(
                "sudo.subprocess.check_call", side_effect=inspect_config
            ) as check_call,
        ):
            assert plugin.handle("sudo", [{"shell": ["true"]}])

        check_call.assert_called_once()
        assert check_call.call_args.kwargs == {}
        args = check_call.call_args.args[0]
        assert args[0] == "sudo"
        assert args[-2] == "--config-file"
        config_path = args[-1]
        assert not Path(config_path).exists()

    def test_handle_returns_false_on_subprocess_failure(self, tmp_path: Path) -> None:
        plugin = Sudo(get_context(tmp_path))

        with (
            patch.object(plugin, "_find_dotbot", return_value="dotbot"),
            patch.object(plugin, "_collect_plugins", return_value=[]),
            patch(
                "sudo.subprocess.check_call",
                side_effect=subprocess.CalledProcessError(1, "sudo"),
            ),
        ):
            assert not plugin.handle("sudo", [])

    def test_written_config_contains_tasks(self, tmp_path: Path) -> None:
        plugin = Sudo(get_context(tmp_path))
        config_path = tmp_path / "config.json"

        plugin._write_conf_file(str(config_path), [{"shell": ["true"]}])

        assert json.loads(config_path.read_text()) == [{"shell": ["true"]}]

    def test_strip_args(self) -> None:
        args = [
            "/home/user/bin/dotbot",
            "-d",
            "/home/user/dotfiles",
            "-p",
            "sudo.py",
            "--verbose",
            "--plugin-dir",
            "plugins",
        ]
        assert Sudo.strip_args(args) == ["--verbose"]

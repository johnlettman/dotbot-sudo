import json
import os
import subprocess
from tempfile import mkstemp
from typing import Any

import dotbot
from dotbot.util import module


class Sudo(dotbot.Plugin):
    """Run a group of Dotbot tasks through sudo."""

    _directive = "sudo"

    def can_handle(self, directive: str) -> bool:
        return directive == self._directive

    def handle(self, directive: str, data: Any) -> bool:
        if directive != self._directive:
            raise ValueError(f"sudo cannot handle directive {directive}")
        if not isinstance(data, list):
            raise TypeError('The "sudo" directive expects a list of tasks')

        config_path: str | None = None
        file_descriptor: int | None = None
        try:
            file_descriptor, config_path = mkstemp(
                prefix="dotbot-sudo.", suffix=".json"
            )
            os.close(file_descriptor)
            file_descriptor = None
            self._log.debug(f"sudo: temporary config path: {config_path}")

            tasks = [{"defaults": self._context.defaults()}] + data
            self._write_conf_file(config_path, tasks)
            proc_args = [
                "sudo",
                self._find_dotbot(),
                "--base-directory",
                self._context.base_directory(),
                "--config-file",
                config_path,
            ] + self._collect_plugins()
            self._log.debug(f"sudo: args to pass: {proc_args}")

            self._log.lowinfo("sudo: begin subprocess")
            # Inherit the terminal so nested package managers can prompt for
            # sudo credentials or PKGBUILD review decisions.
            subprocess.check_call(proc_args)
            self._log.lowinfo("sudo: end subprocess")
            return True
        except subprocess.CalledProcessError as error:
            self._log.lowinfo("sudo: end subprocess")
            self._log.error(error)
            return False
        finally:
            if file_descriptor is not None:
                os.close(file_descriptor)
            if config_path is not None:
                self._log.debug(f"sudo: garbage collecting: {config_path}")
                self._delete_conf_file(config_path)

    def _collect_plugins(self) -> list[str]:
        ret: list[str] = []
        for plugin in module.loaded_modules:
            if plugin.__name__ != self._directive:
                ret.extend(
                    [
                        "--plugin",
                        os.path.splitext(plugin.__file__)[0] + ".py",
                    ]
                )
        return ret

    def _delete_conf_file(self, conf_file: str) -> None:
        if os.path.exists(conf_file):
            os.remove(conf_file)

    def _find_dotbot(self) -> str:
        base = os.path.dirname(os.path.dirname(dotbot.__file__))
        ret = os.path.join(base, "..", "bin", "dotbot")
        self._log.debug(f"sudo: dotbot app path: {ret}")
        return ret

    def _write_conf_file(self, conf_file: str, data: list[dict[str, Any]]) -> None:
        self._delete_conf_file(conf_file)
        with open(conf_file, "w", encoding="utf-8") as jfile:
            json.dump(data, jfile, ensure_ascii=False)

    @staticmethod
    def strip_args(args: list[str]) -> list[str]:
        """Remove Dotbot arguments that the nested invocation must replace."""
        single_args_filter = ["--version", "-h", "--help"]
        double_args_filter = [
            "-d",
            "--base-directory",
            "-c",
            "--config-file",
            "-p",
            "--plugin",
            "--plugin-dir",
        ]

        args_filter = single_args_filter + double_args_filter
        stripped: list[str] = []
        skip = False

        for arg in args:
            if skip:
                skip = False
                continue

            if arg in args_filter:
                skip = arg in double_args_filter
            elif "bin/dotbot" not in arg:
                stripped.append(arg)

        return stripped

import os
import shlex
import shutil
from collections.abc import Iterator
from dataclasses import dataclass, field
from functools import cache
from typing import Any

import cli
from cli.commands.commands import CommandItem

from package_dev_tools.models import Path


@dataclass
class GitInterface:
    path: Path = field(default_factory=Path.cwd)
    git_name: str = "Quinten"
    git_email: str = "quinten.roets@gmail.com"

    def clean(self) -> None:
        self.capture_output("add -A")
        self.capture_output("clean -fd")

    def commit(self, message: str, *, allow_empty: bool = False) -> None:
        self.configure()
        options = "--no-verify --allow-empty" if allow_empty else "--no-verify"
        self.capture_output(f"commit {options} -m", message)

    def generate_files(self, *patterns: str) -> Iterator[Path]:
        return (self.path / path for path in self.generate_relative_files(*patterns))

    def generate_relative_files(self, *patterns: str) -> Iterator[Path]:
        command = "ls-files --cached --others --exclude-standard"
        output = self.capture_output(command, *patterns)
        return (Path(relative_path) for relative_path in output.splitlines())

    def capture_output(self, *args: CommandItem, **kwargs: Any) -> str:
        git_args = f"{resolve_git_binary()} {args[0]}", *args[1:]
        return cli.capture_output(*git_args, cwd=self.path, **kwargs)

    def configure(self) -> None:
        git_configuration = {"name": self.git_name, "email": self.git_email}
        for attribute, value in git_configuration.items():
            self.capture_output(f"config user.{attribute} {value}")


@cache
def resolve_git_binary() -> str:
    paths = (
        path
        for p in os.get_exec_path()
        if (path := shutil.which("git", path=str(p)))
        and not path.startswith(str(Path.home()))
    )
    return shlex.quote(next(paths, shutil.which("git") or "git"))

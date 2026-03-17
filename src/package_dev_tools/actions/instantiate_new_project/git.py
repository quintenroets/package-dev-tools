import os
import shutil
import subprocess
from dataclasses import dataclass, field
from functools import cache
from typing import Any

from cli.commands.run import CommandItem
from cli.commands.runner import Runner

from package_dev_tools.models import Path


@cache
def resolve_git_binary() -> str:
    return next(
        path
        for p in os.get_exec_path()
        if (path := shutil.which("git", path=str(p)))
        and not path.startswith(str(Path.home()))
    )


@dataclass
class GitInterface:
    path: Path = field(default_factory=Path.cwd)
    git_name: str = "Quinten"
    git_email: str = "quinten.roets@gmail.com"
    commit_message: str = "Instantiate new project"

    def clean(self) -> None:
        self.capture_output("add -A")
        self.capture_output("clean -fd")

    def commit(self) -> None:
        self.configure()
        self.capture_output("commit --no-verify -m", self.commit_message)

    def capture_output(self, *args: CommandItem, **kwargs: Any) -> str:
        return self.create_runner(*args, **kwargs).capture_output()

    def run(
        self,
        *args: CommandItem,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:  # pragma: nocover
        return self.create_runner(*args, check=check).run()

    def create_runner(self, *args: CommandItem, **kwargs: Any) -> Runner[str]:
        git_args = f"{resolve_git_binary()} {args[0]}", *args[1:]
        return Runner[str](git_args, kwargs={"cwd": self.path, **kwargs})

    def configure(self) -> None:
        git_configuration = {"name": self.git_name, "email": self.git_email}
        for attribute, value in git_configuration.items():
            self.capture_output(f"config user.{attribute} {value}")

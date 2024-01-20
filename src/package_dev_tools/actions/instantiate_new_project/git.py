import typing
from dataclasses import dataclass, field

import cli

from ...models import Path


@dataclass
class GitInterface:
    path: Path = field(default_factory=Path.cwd)
    git_name: str = "Quinten"
    git_email: str = "quinten.roets@gmail.com"
    commit_message: str = "Instantiate new project"

    def commit(self) -> None:
        self.get("add .")
        self.get("commit --no-verify -m", self.commit_message)

    def get(self, *args: str | Path | int) -> str:
        git_arg = f"git {args[0]}"
        result = cli.get(git_arg, *args[1:], cwd=self.path)
        return typing.cast(str, result)

    def configure(self) -> None:
        git_configuration = {"name": self.git_name, "email": self.git_email}
        for attribute, value in git_configuration.items():
            self.get(f"config --global user.{attribute} {value}")

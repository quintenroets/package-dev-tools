import subprocess
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
        self.run("add .")
        self.run("commit -m", self.commit_message)

    def run(self, *args: str | Path | int) -> str | subprocess.CompletedProcess:
        git_arg = f"git {args[0]}"
        return cli.run(git_arg, *args[1:], cwd=self.path)

    def configure(self) -> None:
        git_configuration = {"name": self.git_name, "email": self.git_email}
        for attribute, value in git_configuration.items():
            self.run(f"config --global user.{attribute} {value}")

import os
from collections.abc import Iterator
from typing import Any

import cli

from package_dev_tools.models import Path


def clone(url: str, path: os.PathLike[str], *options: object) -> None:
    cli.capture_output(("git", "clone"), *options, url, path)  # pragma: nocover


def commit(root: os.PathLike[str], message: str, *, allow_empty: bool = False) -> None:
    options = "--no-verify --allow-empty" if allow_empty else "--no-verify"
    capture_output(root, f"commit {options} -m", message)


def generate_files(root: os.PathLike[str]) -> Iterator[Path]:
    return (Path(root) / path for path in generate_relative_files(root))


def generate_relative_files(root: os.PathLike[str], *patterns: str) -> Iterator[Path]:
    command = "ls-files --cached --others --exclude-standard"
    output = capture_output(root, command, *patterns)
    return map(Path, output.splitlines())


def capture_output(
    root: os.PathLike[str], command: str, *args: object, **kwargs: Any
) -> str:
    email = "quinten.roets@gmail.com"
    options = "-C", root, "-c", "user.name=Quinten", "-c", f"user.email={email}"
    return cli.capture_output("git", *options, *command.split(), *args, **kwargs)

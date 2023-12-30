import pathlib
import shutil
from collections.abc import Iterator

import cli
import pytest
from dev_tools.actions.substitute_template_name import substitute_template_name
from dev_tools.models import Path


@pytest.fixture
def repository_path(tmp_path: pathlib.Path) -> Iterator[Path]:
    shutil.copytree(Path.repository_root, tmp_path, dirs_exist_ok=True)
    path = Path(tmp_path)
    yield path
    path.rmtree()


def test_substitute_template_name(repository_path: Path) -> None:
    project_name = "new-project"
    substitute_template_name(project_name=project_name, path=repository_path)
    path = repository_path / "pyproject.toml"
    assert project_name in path.text


def test_byte_content_skipping(repository_path: Path) -> None:
    path = repository_path / "binary_content"
    path.byte_content = b"\xFF"
    commands = (
        ("git stash",),
        ("git add", path),
        ("git commit --no-verify -m", "add byte file with byte content"),
    )
    for command in commands:
        cli.run(*command, cwd=repository_path)
    test_substitute_template_name(repository_path)

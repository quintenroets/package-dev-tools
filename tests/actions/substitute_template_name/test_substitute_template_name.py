import cli
import pytest

from package_dev_tools.actions.instantiate_new_project.git import GitInterface
from package_dev_tools.actions.instantiate_new_project.substitute_template_name import (
    NameSubstitutor,
)
from package_dev_tools.models import Path


@pytest.mark.usefixtures("repository_path")
def test_substitute_template_name() -> None:
    substitute_and_verify()


def test_byte_content_skipping(repository_path: Path) -> None:
    path = Path("binary_content")
    path.byte_content = b"\xff"
    GitInterface(repository_path).configure()
    commands = (
        ("git add", path),
        ("git commit --no-verify -m", "add byte file with byte content"),
    )
    for command in commands:
        cli.capture_output(*command)
    substitute_and_verify()


def substitute_and_verify() -> None:
    project_name = "package-dev-tools"
    NameSubstitutor(project_name=project_name).run()
    info = Path("pyproject.toml").text
    assert project_name in info

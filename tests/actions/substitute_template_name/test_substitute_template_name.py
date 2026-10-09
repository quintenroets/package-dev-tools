import pytest

from package_dev_tools.actions.instantiate_new_project.substitute_template_name import (
    NameSubstitutor,
)
from package_dev_tools.models import Path
from package_dev_tools.utils import git


@pytest.mark.usefixtures("repository_path")
def test_substitute_template_name() -> None:
    substitute_and_verify()


def test_byte_content_skipping(repository_path: Path) -> None:
    path = Path("binary_content")
    path.byte_content = b"\xff"
    git.capture_output(repository_path, "add", path)
    git.commit(repository_path, "add byte file with byte content")
    substitute_and_verify()


def substitute_and_verify() -> None:
    project_name = "package-dev-tools"
    NameSubstitutor(project_name=project_name).run()
    info = Path("pyproject.toml").text
    assert project_name in info

import cli
import pytest
from package_dev_tools.actions.instantiate_new_project import (
    ProjectInstantiator,
)
from package_dev_tools.models import Path


@pytest.mark.usefixtures("repository_path")
def test_instantiate_new_project() -> None:
    project_name = "package-dev-tools"
    ProjectInstantiator(project_name=project_name).run()
    info = Path("pyproject.toml").text
    assert project_name in info
    readme = Path("README.md").text
    assert "=" not in readme


@pytest.mark.usefixtures("repository_path")
def test_second_application_no_changes() -> None:
    project_name = "package-dev-tools"
    ProjectInstantiator(project_name=project_name).run()
    ProjectInstantiator(project_name=project_name, commit=False).run()
    changes = cli.capture_output("git status --porcelain")
    assert not changes

from collections.abc import Iterator

import pytest
from package_dev_tools.actions.instantiate_new_project.git import GitInterface
from package_dev_tools.actions.template_sync.merge import Merger
from package_dev_tools.models import Path

from tests.conftest import download_repository


@pytest.fixture()
def repository_name() -> str:
    return "cli"


@pytest.fixture()
def template_directory() -> Iterator[Path]:
    yield from clone(
        "python-package-template",
        commit="a24d34470db6860ea3470ae52fa2b4770b4c8af0",
    )


@pytest.fixture()
def repository_directory(repository_name: str) -> Iterator[Path]:
    yield from clone(repository_name, "a965aca767feac0c9438f6d8ada7f7d84e0519da")


def clone(repository: str, commit: str) -> Iterator[Path]:
    directory = Path.tempfile(create=False)
    download_repository(directory, name=repository, depth=None)
    git = GitInterface(directory)
    git.configure()
    git.capture_output("reset --hard", commit)
    with directory:
        yield directory


def test_merge_template_changes(
    template_directory: Path,
    repository_directory: Path,
    repository_name: str,
) -> None:
    merger = Merger(
        repository_directory,
        template_directory,
        repository=repository_name,
    )
    merger.merge_in_template_updates()
    git = GitInterface(repository_directory)
    git.capture_output("add -A")
    status = git.capture_output("status")
    assert "pyproject.toml" in status

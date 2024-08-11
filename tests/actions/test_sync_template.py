from collections.abc import Iterator
from unittest.mock import patch, MagicMock

import pytest
from package_dev_tools.actions.instantiate_new_project.git import GitInterface
from package_dev_tools.actions.template_sync.sync import TemplateSyncer
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


@patch(
    "package_dev_tools.actions.template_sync.sync.TemplateSyncer.push_updates",
)
def test_sync_template(
    patched_push: MagicMock,
    template_directory: Path,
    repository_directory: Path,
    repository_name: str,
    github_token: str,
) -> None:
    patched_repository = patch(
        "package_dev_tools.actions.template_sync.sync.TemplateSyncer.downloaded_repository_directory",
        new=repository_directory,
    )
    patched_template_repository = patch(
        "package_dev_tools.actions.template_sync.sync.TemplateSyncer.downloaded_template_repository_directory",
        new=template_directory,
    )
    with patched_repository, patched_template_repository:
        TemplateSyncer(token=github_token, repository=repository_name).run()
    patched_push.assert_called_once()

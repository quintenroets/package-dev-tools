import shutil
from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest

from package_dev_tools.actions.template_sync.sync import TemplateSyncer
from package_dev_tools.models import Path
from tests import environment

syncer_path = "package_dev_tools.actions.template_sync.sync.TemplateSyncer"
clone_url = "https://github.com/quintenroets/cli.git"


@pytest.fixture
def syncer(
    template_directory: Path,
    repository_directory: Path,
) -> Iterator[TemplateSyncer]:
    mock_repository_client = MagicMock()
    mock_repository_client.clone_url = clone_url
    patched_clone_repository = patch(
        f"{syncer_path}.clone_repository",
        side_effect=lambda path: shutil.copytree(repository_directory, path),
    )
    patched_clone_template = patch(
        f"{syncer_path}.clone_template_repository",
        side_effect=lambda path: shutil.copytree(template_directory, path),
    )
    patched_repository_client = patch(
        f"{syncer_path}.repository_client",
        new=mock_repository_client,
    )
    with patched_clone_repository, patched_clone_template, patched_repository_client:
        yield TemplateSyncer(
            token=environment.github_token(),
            repository="quintenroets/cli",
        )


@patch(f"{syncer_path}.push_updates")
@patch(
    f"{syncer_path}.generate_files_in_template_commit",
    side_effect=lambda: ["pyproject.toml"],
)
def test_sync_template(
    mocked_commit: MagicMock,
    mocked_push: MagicMock,
    syncer: TemplateSyncer,
) -> None:
    syncer.run()
    mocked_commit.assert_called_once()
    mocked_push.assert_called_once()


@patch(f"{syncer_path}.push_updates")
@patch(f"{syncer_path}.generate_files_in_template_commit", side_effect=list)
def test_sync_template_without_changes(
    mocked_commit: MagicMock,
    mocked_push: MagicMock,
    syncer: TemplateSyncer,
) -> None:
    syncer.run()
    mocked_commit.assert_called_once()
    mocked_push.assert_not_called()


def test_project_clone_url(syncer: TemplateSyncer) -> None:
    url = syncer.project_clone_url
    assert f"https://quintenroets:{syncer.token}@" in url


def test_create_pull_request_body(syncer: TemplateSyncer) -> None:
    syncer.latest_commit.commit._message._value = "(#30)"  # type: ignore[attr-defined]  # noqa: SLF001
    body = syncer.create_pull_request_body()
    assert "pull" in body


def test_create_pull_request_body_without_template_pull_request(
    syncer: TemplateSyncer,
) -> None:
    syncer.latest_commit.commit._message._value = "message"  # type: ignore[attr-defined]  # noqa: SLF001
    body = syncer.create_pull_request_body()
    assert "commit" in body

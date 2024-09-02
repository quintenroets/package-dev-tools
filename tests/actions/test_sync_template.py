from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest

from package_dev_tools.actions.template_sync.sync import TemplateSyncer
from package_dev_tools.models import Path

syncer_path = "package_dev_tools.actions.template_sync.sync.TemplateSyncer"


@pytest.fixture
def syncer(
    template_directory: Path,
    repository_directory: Path,
    repository_name: str,
    github_token: str,
) -> Iterator[TemplateSyncer]:
    patched_repository = patch(
        f"{syncer_path}.downloaded_repository_directory",
        new=repository_directory,
    )
    patched_template_repository = patch(
        f"{syncer_path}.downloaded_template_repository_directory",
        new=template_directory,
    )
    with patched_repository, patched_template_repository:
        yield TemplateSyncer(token=github_token, repository=repository_name)


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

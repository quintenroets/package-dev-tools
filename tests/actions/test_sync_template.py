from unittest.mock import MagicMock, patch

from package_dev_tools.actions.template_sync.sync import TemplateSyncer
from package_dev_tools.models import Path


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
    patched_commit = patch(
        "package_dev_tools.actions.template_sync.sync.TemplateSyncer.generate_files_in_template_commit",
        new=["pyproject.toml"],
    )
    with patched_repository, patched_template_repository, patched_commit:
        TemplateSyncer(token=github_token, repository=repository_name).run()
    patched_push.assert_called_once()

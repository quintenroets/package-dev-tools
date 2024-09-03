from collections.abc import Callable
from unittest import mock

import pytest
from package_dev_utils.tests.args import cli_args, no_cli_args

from package_dev_tools.cli import (
    check_coverage,
    check_shields,
    cleanup_readme,
    extract_package_name,
    extract_required_python_version,
    extract_supported_python_versions,
    instantiate_new_project,
    substitute_template_name,
    sync_template,
    trigger_template_sync,
)

entry_points = [
    check_shields.entry_point,
    cleanup_readme.entry_point,
    instantiate_new_project.entry_point,
    extract_package_name.entry_point,
    extract_required_python_version.entry_point,
    extract_supported_python_versions.entry_point,
    substitute_template_name.entry_point,
]


@no_cli_args
@pytest.mark.parametrize("entry_point", entry_points)
@pytest.mark.usefixtures("repository_path")
def test_entry_point(entry_point: Callable[..., None]) -> None:
    entry_point()


@no_cli_args
@pytest.mark.usefixtures("repository_path")
def test_check_coverage() -> None:
    exceptions = SystemExit, Exception
    with pytest.raises(exceptions):
        check_coverage.entry_point()


def test_trigger_template_sync(github_token: str) -> None:
    args = cli_args("--token", github_token)
    patched_workflow = mock.patch("github.Workflow")
    with args, patched_workflow:
        trigger_template_sync.entry_point()


def test_sync_template(github_token: str) -> None:
    repository = "quintenroets/package-dev-tools"
    args = cli_args("--token", github_token, "--repository", repository)
    patched_push = mock.patch(
        "package_dev_tools.actions.template_sync.sync.TemplateSyncer.push_updates",
    )
    with args, patched_push:
        sync_template.entry_point()

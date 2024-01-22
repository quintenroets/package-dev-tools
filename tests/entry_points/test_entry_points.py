import os
import typing
from collections.abc import Callable
from unittest import mock

import cli
import pytest
from package_dev_tools.cli import (
    check_coverage,
    check_shields,
    cleanup_readme,
    extract_package_name,
    extract_required_python_version,
    extract_supported_python_versions,
    instantiate_new_project,
    substitute_template_name,
    trigger_template_sync,
)
from package_dev_tools.models import Path
from package_dev_utils.tests.args import cli_args, no_cli_args

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
def test_entry_point(entry_point: Callable[..., None], repository_path: Path) -> None:
    entry_point()


@no_cli_args
def test_check_coverage(repository_path: Path) -> None:
    exceptions = SystemExit, Exception
    with pytest.raises(exceptions):  # noqa
        check_coverage.entry_point()


def test_trigger_template_sync() -> None:
    token_name = "TEMPLATE_SYNC_TRIGGER_TOKEN"
    token = os.environ.get(token_name) or cli.get("pw", "automationtoken")
    token = typing.cast(str, token)
    args = cli_args("--token", token)
    patched_workflow = mock.patch("github.Workflow")
    with args, patched_workflow:
        trigger_template_sync.entry_point()

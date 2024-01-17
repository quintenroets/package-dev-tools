import os
from unittest import mock

import cli
import pytest
from package_dev_tools.cli import (
    check_coverage,
    cleanup_readme,
    instantiate_new_project,
    substitute_template_name,
    trigger_template_sync,
)
from package_dev_tools.models import Path
from package_dev_utils.tests.args import cli_args, no_cli_args


@no_cli_args
def test_check_coverage(repository_path: Path) -> None:
    exceptions = SystemExit, Exception
    with pytest.raises(exceptions):  # noqa
        check_coverage.entry_point()


@cli_args("--project-name", "package-dev-tools")
def test_substitute_template_name(repository_path: Path) -> None:
    substitute_template_name.entry_point()


@no_cli_args
def test_cleanup_readme(repository_path: Path) -> None:
    cleanup_readme.entry_point()


@no_cli_args
def test_instantiate_new_project(repository_path: Path) -> None:
    instantiate_new_project.entry_point()


def test_trigger_template_sync() -> None:
    token_name = "TEMPLATE_SYNC_TRIGGER_TOKEN"
    token = os.environ.get(token_name) or cli.get("pw", "automationtoken")
    args = cli_args("--token", token)
    patched_workflow = mock.patch("github.Workflow")
    with args, patched_workflow:
        trigger_template_sync.entry_point()

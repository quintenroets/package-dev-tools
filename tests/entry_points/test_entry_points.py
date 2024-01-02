import os
from unittest import mock

import cli
import pytest
from _pytest.monkeypatch import MonkeyPatch
from dev_tools.interfaces.cli import (
    check_coverage,
    cleanup_readme,
    substitute_template_name,
    trigger_template_sync,
)
from dev_tools.models import Path
from dev_tools.utils.tests import clear_cli_args, set_cli_args


def test_check_coverage(repository_path: Path, monkeypatch: MonkeyPatch) -> None:
    clear_cli_args(monkeypatch)
    exceptions = SystemExit, Exception
    with pytest.raises(exceptions):  # noqa
        check_coverage.entry_point()


def test_substitute_template_name(
    repository_path: Path, monkeypatch: MonkeyPatch
) -> None:
    set_cli_args(monkeypatch, "--project-name", "dev-tools")
    with pytest.raises(SystemExit):
        substitute_template_name.entry_point()


def test_cleanup_readme(repository_path: Path, monkeypatch: MonkeyPatch) -> None:
    clear_cli_args(monkeypatch)
    with pytest.raises(SystemExit):
        cleanup_readme.entry_point()


def test_trigger_template_sync(monkeypatch: MonkeyPatch) -> None:
    token_name = "TEMPLATE_SYNC_TRIGGER_TOKEN"
    token = os.environ.get(token_name) or cli.get("pw", "automationtoken")
    set_cli_args(monkeypatch, token)
    with mock.patch("github.Workflow"), pytest.raises(SystemExit):
        trigger_template_sync.entry_point()

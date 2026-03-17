from collections.abc import Callable, Iterator
from contextlib import contextmanager
from unittest import mock
from unittest.mock import patch

import pytest
from package_dev_utils.tests.args import cli_args, no_cli_args

from package_dev_tools.cli import (
    check_coverage,
    check_shields,
    cleanup_readme,
    export_pre_commit_config,
    extract_package_name,
    extract_required_python_version,
    extract_supported_python_versions,
    instantiate_new_project,
    substitute_template_name,
    sync_template,
    trigger_template_sync,
)
from package_dev_tools.models import Path
from package_dev_tools.pre_commit import check_import
from tests import environment

syncer_path = "package_dev_tools.actions.template_sync.sync.TemplateSyncer"


@contextmanager
def with_syncer_directories(repository: Path, template: Path) -> Iterator[None]:
    repo_dir = f"{syncer_path}.downloaded_repository_directory"
    template_dir = f"{syncer_path}.downloaded_template_repository_directory"
    with mock.patch(repo_dir, new=repository), mock.patch(template_dir, new=template):
        yield


entry_points = [
    check_shields.entry_point,
    cleanup_readme.entry_point,
    instantiate_new_project.entry_point,
    extract_package_name.entry_point,
    extract_required_python_version.entry_point,
    extract_supported_python_versions.entry_point,
    substitute_template_name.entry_point,
    export_pre_commit_config.entry_point,
    check_import.entry_point,
]


@no_cli_args
@pytest.mark.parametrize("entry_point", entry_points)
@pytest.mark.usefixtures("repository_path")
def test_entry_point(entry_point: Callable[..., None]) -> None:
    with patch("importlib.import_module"):
        entry_point()


@no_cli_args
@pytest.mark.usefixtures("repository_path")
def test_export_pre_commit_config_with_seed() -> None:
    seed_file = Path("config/pre-commit-seed.yaml")
    seed_file.create_parent()
    seed_file.yaml = [{"entry": "ruff", "args": ["check", "."]}]
    with patch("importlib.import_module"):
        export_pre_commit_config.entry_point()


@no_cli_args
@pytest.mark.usefixtures("repository_path")
def test_check_coverage() -> None:
    exceptions = SystemExit, Exception
    with pytest.raises(exceptions):
        check_coverage.entry_point()


def test_trigger_template_sync() -> None:
    args = cli_args("--token", environment.github_token())
    patched_workflow = mock.patch("github.Workflow")
    with args, patched_workflow:
        trigger_template_sync.entry_point()


def test_sync_template(template_directory: Path, repository_directory: Path) -> None:
    repository = "quintenroets/package-dev-tools"
    args = cli_args("--token", environment.github_token(), "--repository", repository)
    patched_push = mock.patch(f"{syncer_path}.push_updates")
    directories = with_syncer_directories(repository_directory, template_directory)
    with args, patched_push, directories:
        sync_template.entry_point()

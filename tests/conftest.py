import os
import pathlib
import shutil
from collections.abc import Iterator

import cli
import pytest
from _pytest.tmpdir import TempPathFactory
from hypothesis import HealthCheck
from package_dev_tools.actions.instantiate_new_project.git import GitInterface
from package_dev_tools.models import Path

suppressed_checks = (HealthCheck.function_scoped_fixture,)


@pytest.fixture(scope="session")
def downloaded_repository_path(tmp_path_factory: TempPathFactory) -> Iterator[Path]:
    tmp_path = tmp_path_factory.mktemp("_")
    path = Path(tmp_path)
    repository_url = "https://github.com/quintenroets/python-package-template"
    git_interface = GitInterface()
    git_interface.configure()
    git_interface.get("clone", repository_url, path, "--depth", 1)
    generate_coverage_results(path)
    yield path
    path.rmtree()


def generate_coverage_results(path: Path) -> None:
    venv_name = "test_repository_venv"
    cli.get("python -m venv", venv_name, cwd=path)
    running_on_windows = os.name == "nt"
    bin_name = "Scripts" if running_on_windows else "bin"
    bin_path = path / venv_name / bin_name
    pip = "pip.exe" if running_on_windows else "pip"
    coverage = "coverage.exe" if running_on_windows else "coverage"

    cli.get(bin_path / pip, "install", "-e", ".[dev]", cwd=path)
    cli.get(bin_path / coverage, "run", cwd=path)


@pytest.fixture
def repository_path(
    downloaded_repository_path: Path, tmp_path: pathlib.Path
) -> Iterator[Path]:
    shutil.copytree(downloaded_repository_path, tmp_path, dirs_exist_ok=True)
    path = Path(tmp_path)
    cwd = Path.cwd()
    os.chdir(path)
    yield path
    os.chdir(cwd)
    path.rmtree()

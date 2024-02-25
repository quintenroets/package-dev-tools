import os
import shutil
import typing
from collections.abc import Callable, Iterator

import cli
import pytest
from package_dev_tools.actions.instantiate_new_project.git import GitInterface
from package_dev_tools.models import Path

running_on_windows = os.name == "nt"
bin_name = "Scripts" if running_on_windows else "bin"
pip = "pip.exe" if running_on_windows else "pip"


@pytest.fixture(scope="session")
def downloaded_repository_path() -> Iterator[Path]:
    with Path.tempfile() as path:
        create_processed_repository(path)
        yield path


@pytest.fixture(scope="session")
def downloaded_repository_path_with_uncovered_files() -> Iterator[Path]:
    with Path.tempfile() as path:
        create_processed_repository(path, callback=add_uncovered_files)
        yield path


def create_processed_repository(
    path: Path, callback: Callable[[Path], None] | None = None
) -> None:
    path.unlink()
    download_repository(path)
    if callback is not None:
        callback(path)
    generate_coverage_results(path)


def download_repository(path: Path) -> None:
    repository_url = "https://github.com/quintenroets/python-package-template"
    git_interface = GitInterface()
    git_interface.configure()
    git_interface.get("clone", repository_url, path, "--depth", 1)


def generate_coverage_results(path: Path) -> None:
    bin_path = get_bin_path(path)
    coverage = "coverage.exe" if running_on_windows else "coverage"
    cli.get(bin_path / pip, "install", "--no-deps", "-e", ".", cwd=path)
    cli.get(bin_path / coverage, "run", cwd=path)


@pytest.fixture
def repository_path(downloaded_repository_path: Path) -> Iterator[Path]:
    yield from use_in_temporary_location(downloaded_repository_path)


@pytest.fixture
def repository_path_with_uncovered_files(
    downloaded_repository_path_with_uncovered_files: Path,
) -> Iterator[Path]:
    yield from use_in_temporary_location(
        downloaded_repository_path_with_uncovered_files
    )


def use_in_temporary_location(source_path: Path) -> Iterator[Path]:
    with Path.tempfile(create=False) as path:
        shutil.copytree(source_path, path)
        cwd = Path.cwd()
        os.chdir(path)
        yield path
        os.chdir(cwd)


def add_uncovered_files(path: Path) -> None:
    not_covered_path = path / "not_covered_file.py"
    not_covered_path.touch()
    test_path = path / "tests" / "test_not_executed_test.py"
    test_path.lines = ("def run():", "\tpass")  # type: ignore


def get_bin_path(repository_path: Path) -> Path:
    env_cache_path = (
        Path.HOME / ".cache" / "pytest-package-dev-tools" / "test_repository_dev_env"
    )
    bin_path = env_cache_path / bin_name
    if not bin_path.exists():
        create_bin_path(env_cache_path, repository_path)  # pragma: nocover, cached
    return typing.cast(Path, bin_path)


def create_bin_path(
    path: Path, repository_path: Path
) -> None:  # pragma: nocover, cached
    path.create_parent()
    cli.get("python -m venv", path.name, cwd=path.parent)
    bin_path = path / bin_name
    cli.get(bin_path / pip, "install", "-e", ".[dev]", cwd=repository_path)

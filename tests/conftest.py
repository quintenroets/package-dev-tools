import os
import shutil
import typing
from collections.abc import Callable, Iterator

import cli
import pytest

from package_dev_tools.actions.instantiate_new_project.git import GitInterface
from package_dev_tools.models import Path

if typing.TYPE_CHECKING:
    from cli.commands.run import CommandItem  # pragma: nocover

running_on_windows = os.name == "nt"
bin_name = "Scripts" if running_on_windows else "bin"
pip = "pip.exe" if running_on_windows else "pip"


@pytest.fixture(scope="session")
def github_token() -> str:
    key = "TEMPLATE_SYNC_TRIGGER_TOKEN"
    return os.environ.get(key) or cli.capture_output("pw", "automationtoken")


@pytest.fixture(scope="session")
def downloaded_repository_path() -> Iterator[Path]:
    with Path.tempfile() as path:
        create_processed_repository(path)
        yield path


@pytest.fixture(scope="session")
def downloaded_repository_path_with_uncovered_files(
    github_token: str,
) -> Iterator[Path]:
    with Path.tempfile() as path:
        create_processed_repository(
            path,
            callback=add_uncovered_files,
            github_token=github_token,
        )
        yield path


def create_processed_repository(
    path: Path,
    callback: Callable[[Path], None] | None = None,
    github_token: str | None = None,
) -> None:
    path.unlink()
    download_repository(path, github_token=github_token)
    if callback is not None:
        callback(path)
    generate_coverage_results(path)


def download_repository(
    path: Path,
    name: str = "python-package-template",
    depth: int | None = 1,
    github_token: str | None = None,
) -> None:
    repository_url = f"https://github.com/quintenroets/{name}"
    if github_token is not None:
        host = "github.com"
        repository_url = repository_url.replace(host, github_token + "@" + host)
    git_interface = GitInterface()
    git_interface.configure()

    command: tuple[CommandItem, ...] = ("clone", repository_url, path)
    if depth is not None:
        command = (*command, "--depth", depth)
    git_interface.capture_output(*command)


def generate_coverage_results(path: Path) -> None:
    bin_path = get_bin_path(path)
    coverage = "coverage.exe" if running_on_windows else "coverage"
    cli.capture_output(bin_path / pip, "install", "--no-deps", "-e", ".", cwd=path)
    cli.capture_output(bin_path / coverage, "run", cwd=path)


@pytest.fixture
def repository_path(downloaded_repository_path: Path) -> Iterator[Path]:
    yield from use_in_temporary_location(downloaded_repository_path)


@pytest.fixture
def repository_path_with_uncovered_files(
    downloaded_repository_path_with_uncovered_files: Path,
) -> Iterator[Path]:
    yield from use_in_temporary_location(
        downloaded_repository_path_with_uncovered_files,
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
    test_path.lines = ("def run():", "\tpass")  # type: ignore[assignment]


def get_bin_path(repository_path: Path) -> Path:
    env_cache_path = (
        Path.HOME / ".cache" / "pytest-package-dev-tools" / "test_repository_dev_env"
    )
    bin_path = env_cache_path / bin_name
    if not bin_path.exists():
        create_bin_path(env_cache_path, repository_path)  # pragma: nocover, cached
    return typing.cast(Path, bin_path)


def create_bin_path(
    path: Path,
    repository_path: Path,
) -> None:  # pragma: nocover, cached
    path.create_parent()
    cli.capture_output("python -m venv", path.name, cwd=path.parent)
    bin_path = path / bin_name
    cli.capture_output(bin_path / pip, "install", "-e", ".[dev]", cwd=repository_path)


@pytest.fixture
def repository_name() -> str:
    return "cli"


@pytest.fixture
def template_directory() -> Iterator[Path]:
    yield from clone(
        "python-package-template",
        commit="a24d34470db6860ea3470ae52fa2b4770b4c8af0",
    )


@pytest.fixture
def repository_directory(repository_name: str) -> Iterator[Path]:
    yield from clone(repository_name, "a965aca767feac0c9438f6d8ada7f7d84e0519da")


def clone(repository: str, commit: str) -> Iterator[Path]:
    directory = Path.tempfile(create=False)
    download_repository(directory, name=repository, depth=None)
    git = GitInterface(directory)
    git.configure()
    git.capture_output("reset --hard", commit)
    with directory:
        yield directory

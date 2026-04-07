import os
import shutil
from collections.abc import Iterator
from functools import cache
from typing import TYPE_CHECKING, cast

import cli
from simple_classproperty import classproperty

from package_dev_tools.actions.instantiate_new_project.git import GitInterface
from package_dev_tools.models import Path

if TYPE_CHECKING:
    from cli.commands.run import CommandItem  # pragma: nocover


class Commits:
    template = "907dec3b8b5a0f45b9d29e4e6ef5e32b3b73c83d"
    cli = "a8e24ea4eef62d0e19f92fefd1ff28628620a40d"


@cache
def github_token() -> str:
    key = "TEMPLATE_SYNC_TRIGGER_TOKEN"
    return os.environ.get(key) or cli.capture_output("pw", "automationtoken")


running_on_windows = os.name == "nt"
bin_name = "Scripts" if running_on_windows else "bin"
pip = "pip.exe" if running_on_windows else "pip"
coverage = "coverage.exe" if running_on_windows else "coverage"


class Paths:
    @classproperty
    def cache(cls) -> Path:
        return cast("Path", Path.HOME / ".cache" / "pytest-package-dev-tools")

    @classproperty
    def dev_env(cls) -> Path:  # pragma: nocover, cached
        return cast("Path", cls.cache / "test_repository_dev_env")


def generate_coverage_results(path: Path) -> None:  # pragma: nocover, cached
    bin_path = prepare_bin_path(path)
    cli.capture_output(bin_path / pip, "install", "--no-deps", "-e", ".", cwd=path)
    cli.capture_output(bin_path / coverage, "run", cwd=path)


def prepare_bin_path(repository_path: Path) -> Path:  # pragma: nocover, cached
    bin_path = Paths.dev_env / bin_name
    if not (bin_path / coverage).exists():
        create_bin_path(Paths.dev_env, repository_path)
    return cast("Path", bin_path)


def create_bin_path(
    path: Path,
    repository_path: Path,
) -> None:  # pragma: nocover, cached
    path.create_parent()
    cli.capture_output("python -m venv", path.name, cwd=path.parent)
    bin_path = path / bin_name
    package_dev_tools_root = Path(__file__).parent.parent
    cli.capture_output(bin_path / pip, "install", "-e", package_dev_tools_root)
    cli.capture_output(bin_path / pip, "install", "-e", ".[dev]", cwd=repository_path)


def locate_processed_repository(*, with_uncovered_files: bool = False) -> Path:
    suffix = "-uncovered" if with_uncovered_files else ""
    create = (
        create_uncovered_processed_repository
        if with_uncovered_files
        else create_processed_repository
    )
    cache_path = cast(
        "Path",
        Paths.cache / f"python-package-template-processed{suffix}",
    )
    if not (cache_path / "pyproject.toml").exists():  # pragma: nocover, cached
        create(cache_path)
    return cache_path


def create_uncovered_processed_repository(
    path: Path,
) -> None:  # pragma: nocover, cached
    shutil.copytree(locate_processed_repository(), path)
    (path / "not_covered_file.py").touch()
    test_path = path / "tests" / "test_not_executed_test.py"
    test_path.lines = ("def run():", "\tpass")
    generate_coverage_results(path)


def create_processed_repository(path: Path) -> None:  # pragma: nocover, cached
    download_repository(path)
    generate_coverage_results(path)


def download_repository(
    path: Path,
    name: str = "python-package-template",
    depth: int | None = 1,
) -> None:  # pragma: nocover, cached
    token = github_token()
    repository_url = f"https://github.com/quintenroets/{name}"
    if token:
        host = "github.com"
        repository_url = repository_url.replace(host, token + "@" + host)
    git_interface = GitInterface()
    git_interface.configure()

    command: tuple[CommandItem, ...] = ("clone", repository_url, path)
    if depth is not None:
        command = (*command, "--depth", depth)
    git_interface.capture_output(*command)


def locate_cached_checkout(name: str, commit: str) -> Path:
    cache_path = Paths.cache / f"{name}-{commit[:8]}"
    if not (cache_path / ".git").exists():  # pragma: nocover, cached
        download_to_cache(cache_path, name, commit)
    return cast("Path", cache_path)


def download_to_cache(  # pragma: nocover, cached
    path: Path,
    name: str,
    commit: str,
) -> None:
    download_repository(path, name=name, depth=None)
    git = GitInterface(path)
    git.configure()
    git.capture_output("reset --hard", commit)


def create_temporary_copy(source_path: Path) -> Iterator[Path]:
    with Path.tempfile(create=False) as path:
        shutil.copytree(source_path, path)
        cwd = Path.cwd()
        os.chdir(path)
        try:
            yield path
        finally:
            os.chdir(cwd)


def create_cached_checkout(name: str, commit: str) -> Iterator[Path]:
    yield from create_worktree(locate_cached_checkout(name, commit))


def create_worktree(source_path: Path) -> Iterator[Path]:
    path = Path.tempfile(create=False)
    git = GitInterface(source_path)
    git.capture_output("worktree add --detach", path)
    try:
        yield path
    finally:
        git.capture_output("worktree remove --force", path)
        git.capture_output("worktree prune")

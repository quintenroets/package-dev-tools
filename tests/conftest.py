from collections.abc import Iterator

import pytest

from package_dev_tools.models import Path
from tests import environment


@pytest.fixture(scope="session")
def downloaded_repository_path() -> Path:
    return environment.locate_processed_repository()


@pytest.fixture(scope="session")
def downloaded_repository_path_with_uncovered_files() -> Path:
    return environment.locate_processed_repository(with_uncovered_files=True)


@pytest.fixture
def repository_path(downloaded_repository_path: Path) -> Iterator[Path]:
    yield from environment.create_temporary_copy(downloaded_repository_path)


@pytest.fixture
def repository_path_with_uncovered_files(
    downloaded_repository_path_with_uncovered_files: Path,
) -> Iterator[Path]:
    yield from environment.create_temporary_copy(
        downloaded_repository_path_with_uncovered_files,
    )


@pytest.fixture
def template_directory() -> Iterator[Path]:
    yield from environment.create_cached_checkout(
        "python-package-template",
        environment.Commits.template,
    )


@pytest.fixture
def repository_directory() -> Iterator[Path]:
    yield from environment.create_cached_checkout("cli", environment.Commits.cli)

from collections.abc import Iterator
from unittest.mock import Mock, patch

import pytest

from package_dev_tools.models import Path
from tests import environment


@pytest.fixture(autouse=True)
def released_versions() -> Iterator[None]:
    latest_minor_version = 14
    install_manager_release = {"name": "Python install manager 26.3", "version": 100}
    releases = (
        {"name": f"Python 3.{minor_version}.0", "version": 3}
        for minor_version in range(latest_minor_version + 1)
    )
    response = Mock()
    response.json.return_value = [*releases, install_manager_release]
    get = "package_dev_tools.utils.python_versions.requests.get"
    with patch(get, return_value=response):
        yield


@pytest.fixture(scope="session")
def downloaded_repository_path() -> Path:
    return environment.locate_processed_repository()


@pytest.fixture
def repository_path(downloaded_repository_path: Path) -> Iterator[Path]:
    yield from environment.create_temporary_copy(downloaded_repository_path)


@pytest.fixture
def template_directory() -> Iterator[Path]:
    yield from environment.create_cached_checkout(
        "python-package-template",
        environment.Commits.template,
    )


@pytest.fixture
def repository_directory() -> Iterator[Path]:
    yield from environment.create_cached_checkout("cli", environment.Commits.cli)

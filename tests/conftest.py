import os
import pathlib
import shutil
from collections.abc import Iterator

import cli
import pytest
from _pytest.tmpdir import TempPathFactory
from hypothesis import HealthCheck
from package_dev_tools.models import Path

suppressed_checks = (HealthCheck.function_scoped_fixture,)


@pytest.fixture(scope="session")
def downloaded_repository_path(tmp_path_factory: TempPathFactory) -> Iterator[Path]:
    tmp_path = tmp_path_factory.mktemp("_")
    path = Path(tmp_path)
    repository_url = "https://github.com/quintenroets/python-package-template"
    commands = (
        ("git config --global user.email quinten.roets@gmail.com",),
        ("git config --global user.name Quinten",),
        ("git clone", repository_url, tmp_path, "--depth", 1),
    )
    for command in commands:
        cli.get(*command)
    cli.get("coverage run", cwd=tmp_path)
    yield path
    path.rmtree()


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

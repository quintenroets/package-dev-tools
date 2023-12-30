import os
import pathlib
import shutil
from collections.abc import Iterator

import cli
import pytest
from hypothesis import HealthCheck

from dev_tools.models import Path

suppressed_checks = (HealthCheck.function_scoped_fixture,)


@pytest.fixture
def restore_readme() -> Iterator[None]:
    saved_content = Path.readme.text
    yield
    Path.readme.text = saved_content


@pytest.fixture
def repository_path(tmp_path: pathlib.Path) -> Iterator[Path]:
    shutil.copytree(Path.repository_root, tmp_path, dirs_exist_ok=True)
    path = Path(tmp_path)
    cwd = Path.cwd()
    os.chdir(path)
    cli.get("git stash")
    print(list(path.iterdir()))
    yield path
    os.chdir(cwd)
    path.rmtree()

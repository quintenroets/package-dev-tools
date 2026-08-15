import re

import pytest

from package_dev_tools.models import Path
from package_dev_tools.pre_commit.check_coverage import check_coverage
from package_dev_tools.utils.badge import Badge, BadgeUpdater
from package_dev_tools.utils.git import GitInterface

untested_file_name = "untested_file.py"


@pytest.mark.usefixtures("repository_path")
@pytest.mark.parametrize("track_file", [True, False])
def test_untested_files_detected(
    capfd: pytest.CaptureFixture[str],
    *,
    track_file: bool,
) -> None:
    create_untested_file()
    if track_file:
        GitInterface().capture_output("add -A")
    message = "is below the required"
    with pytest.raises(Exception, match=message):
        check_coverage()
    assert untested_file_name in capfd.readouterr().out


@pytest.mark.usefixtures("repository_path")
def test_run_omitted_files_ignored() -> None:
    create_untested_file()
    path = Path("pyproject.toml")
    omit_configuration = f'[tool.coverage.run]\nomit = ["{untested_file_name}"]'
    path.text = path.text.replace("[tool.coverage.run]", omit_configuration)
    with pytest.raises(SystemExit) as exception:
        check_coverage()
    assert exception.value.code == 0


def create_untested_file() -> None:
    Path(untested_file_name).lines = ("def run():", "\tpass")


@pytest.mark.usefixtures("repository_path")
def test_missing_results_detected() -> None:
    Path(".coverage").unlink()
    message = "No coverage results found."
    with pytest.raises(Exception, match=message):
        check_coverage()


def test_badge_missing_in_readme_indicated(repository_path: Path) -> None:
    (repository_path / Path.readme.name).text = ""
    with pytest.raises(Exception, match=re.escape("README has no Coverage badge yet.")):
        check_coverage()


@pytest.mark.usefixtures("repository_path")
def test_exit_code_reflects_badge_change() -> None:
    BadgeUpdater(Badge("Coverage", "coverage-0%25")).run()
    with pytest.raises(SystemExit) as exception:
        check_coverage()
    assert exception.value.code == 1
    with pytest.raises(SystemExit) as exception:
        check_coverage()
    assert exception.value.code == 0

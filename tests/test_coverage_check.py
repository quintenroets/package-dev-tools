import cli
import pytest
from hypothesis import HealthCheck, given, settings, strategies

from dev_tools.models import Path
from dev_tools.pre_commit.check_coverage import check_coverage, update_coverage_shield

suppressed_checks = (HealthCheck.function_scoped_fixture,)


@given(value=strategies.integers(min_value=0, max_value=100))
@settings(suppress_health_check=suppressed_checks)
def test_update_coverage_badge(restore_readme: None, value: int) -> None:
    update_coverage_shield(value)
    assert str(value) in Path.readme.text


def test_not_covered_files_detected(repository_path: Path) -> None:
    path = repository_path / "not_covered_file.py"
    path.touch()
    commands = (
        ("git add", path),
        ("git commit --no-verify -m", "add not covered file"),
    )
    for command in commands:
        cli.run(*command)

    with pytest.raises(Exception):
        check_coverage()


def test_check_coverage_changed(restore_readme: None) -> None:
    update_coverage_shield(-1)
    with pytest.raises(SystemExit) as exception:
        check_coverage()
    assert exception.value.code == 1


def test_check_coverage_when_unchanged(restore_readme: None) -> None:
    with pytest.raises(SystemExit):
        check_coverage()
    with pytest.raises(SystemExit) as exception:
        check_coverage()
    assert exception.value.code == 0  # status code 0 if coverage not changed

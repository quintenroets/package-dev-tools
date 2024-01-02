import cli
import pytest
from dev_tools.models import Path
from dev_tools.pre_commit.check_coverage import check_coverage, update_coverage_shield
from hypothesis import HealthCheck, given, settings, strategies

suppressed_checks = (HealthCheck.function_scoped_fixture,)


@given(value=strategies.floats(min_value=0, max_value=100))
@settings(suppress_health_check=suppressed_checks)
def test_update_coverage_badge(repository_path: Path, value: float) -> None:
    update_coverage_shield(value)
    readme_path = repository_path / Path.readme.name
    value_str = str(round(value))
    assert value_str in readme_path.text


def test_not_covered_files_detected(repository_path: Path) -> None:
    path = repository_path / "not_covered_file.py"
    path.touch()
    commands = (
        ("git add", path),
        ("git commit --no-verify -m", "add not covered file"),
    )
    for command in commands:
        cli.get(*command)

    with pytest.raises(Exception):
        check_coverage()


def test_badge_missing_in_readme_indicated(repository_path: Path) -> None:
    (repository_path / Path.readme.name).text = ""
    with pytest.raises(Exception, match="README has no coverage badge yet."):
        check_coverage(verify_all_files_tested=False)


def test_check_coverage_when_changed(repository_path: Path) -> None:
    verify_coverage_when_changed()


def test_check_coverage_when_unchanged(repository_path: Path) -> None:
    verify_all_files_tested = False
    with pytest.raises(SystemExit):
        check_coverage(verify_all_files_tested=verify_all_files_tested)
    with pytest.raises(SystemExit) as exception:
        check_coverage(verify_all_files_tested=verify_all_files_tested)
    assert exception.value.code == 0  # status code 0 if coverage not changed


def test_check_coverage_when_installed(repository_path: Path) -> None:
    cli.run("pip install", repository_path)
    verify_coverage_when_changed()


def verify_coverage_when_changed() -> None:
    update_coverage_shield(-1)
    with pytest.raises(SystemExit) as exception:
        check_coverage(verify_all_files_tested=False)
    assert exception.value.code == 1


@given(
    value=strategies.floats(min_value=0, max_value=100),
    new_value=strategies.floats(min_value=0, max_value=100),
)
@settings(suppress_health_check=suppressed_checks)
def test_readme_content_preserved(
    value: float, new_value: float, repository_path: Path
) -> None:
    update_coverage_shield(value)
    readme_length = len(Path.readme.text)
    update_coverage_shield(new_value)
    new_readme_length = len(Path.readme.text)
    length_change = readme_length - new_readme_length
    value_length_change = len(str(round(value))) - len(str(round(new_value)))
    assert length_change == value_length_change

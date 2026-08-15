import sys
from io import StringIO

import cli
from coverage import Coverage
from coverage.results import should_fail_under

from package_dev_tools.models import Path
from package_dev_tools.utils.badge import Badge, BadgeUpdater
from package_dev_tools.utils.git import GitInterface


def check_coverage() -> None:
    coverage = load_coverage()
    files = [str(path) for path in GitInterface().generate_project_files("*.py")]
    percentage = coverage.report(files, ignore_errors=True, file=StringIO())
    verify_fail_under(coverage, files, percentage)
    has_changed = update_badge(coverage, files, percentage)
    sys.exit(1 if has_changed else 0)


def load_coverage() -> Coverage:
    coverage = Coverage()
    if not Path(coverage.config.data_file).exists():
        message = "No coverage results found."
        raise FileNotFoundError(message)
    coverage.load()
    config = coverage.config
    config.report_omit = [*config.run_omit, *(config.report_omit or [])]
    return coverage


def verify_fail_under(coverage: Coverage, files: list[str], percentage: float) -> None:
    config = coverage.config
    if should_fail_under(percentage, config.fail_under, config.precision):
        coverage.html_report(files, ignore_errors=True)
        coverage.report(files, show_missing=True, ignore_errors=True)
        current = format_percentage(percentage, config.precision)
        required = format_percentage(config.fail_under, config.precision)
        message = f"Coverage {current} is below the required {required}"
        raise RuntimeError(message)


def update_badge(coverage: Coverage, files: list[str], percentage: float) -> bool:
    badge = Badge("Coverage", f"coverage-{round(percentage)}%25")
    has_changed = BadgeUpdater(badge).run()
    if has_changed:
        formatted_percentage = format_percentage(percentage, coverage.config.precision)
        cli.console.print(f"Updated test coverage: {formatted_percentage}")
        coverage.html_report(files, ignore_errors=True)
    return has_changed


def format_percentage(value: float, precision: int) -> str:
    return f"{value:.{precision}f}%"

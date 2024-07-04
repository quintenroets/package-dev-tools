import sys
from collections.abc import Iterator

import cli

from package_dev_tools.models import Path
from package_dev_tools.utils.badge import Badge, BadgeUpdater


def check_coverage(*, verify_all_files_tested: bool = True) -> None:
    verify_coverage_results()
    if verify_all_files_tested:
        verify_all_python_files_tested()

    try:
        coverage_percentage = cli.capture_output("coverage report -i --format total")
    except cli.CalledProcessError:
        cli.capture_output("coverage html -i", check=False)
        cli.run("coverage report -mi", check=False)
        raise
    coverage_percentage_has_changed = update_coverage_shield(coverage_percentage)
    if coverage_percentage_has_changed:
        cli.console.print(f"Updated test coverage: {coverage_percentage}%")
        cli.capture_output("coverage html")
    exit_code = 1 if coverage_percentage_has_changed else 0
    sys.exit(exit_code)


def update_coverage_shield(coverage_percentage: float | str) -> bool:
    if isinstance(coverage_percentage, str):
        coverage_percentage = float(coverage_percentage)
    coverage_percentage_int = round(coverage_percentage)
    badge = Badge("Coverage", f"coverage-{coverage_percentage_int}%25")
    return BadgeUpdater(badge).run()


def verify_all_python_files_tested() -> None:
    python_files = set(generate_python_files())
    coverage_lines = cli.capture_output_lines("coverage report -i", check=False)
    covered_files = {line.split()[0] for line in coverage_lines[2:-2]}
    not_covered_files = python_files - covered_files
    if not_covered_files:
        cli.run("coverage html -i", check=False)
        message_parts = (
            "The following files are not covered by tests:",
            *not_covered_files,
        )
        message = "\n\t".join(message_parts)
        raise RuntimeError(message)


def generate_python_files() -> Iterator[str]:
    project_folder = Path.cwd()
    python_files = project_folder.rglob("*.py")
    for path in python_files:
        relative_path = path.relative_to(project_folder)
        if relative_path.parts[0] not in ("build", ".venv"):
            yield str(relative_path)


def verify_coverage_results() -> None:
    if not Path(".coverage").exists():
        message = "No coverage results found."
        raise OSError(message)

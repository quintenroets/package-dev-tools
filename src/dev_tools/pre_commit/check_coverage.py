import sys

import cli

from ..models import Path


def check_coverage() -> None:
    verify_all_files_tested()
    coverage_percentage = cli.get("coverage report --format total")
    coverage_percentage_has_changed = update_coverage_shield(coverage_percentage)
    if coverage_percentage_has_changed:
        print(f"Updated test coverage: {coverage_percentage}%")
        cli.get("coverage html")
    exit_code = 1 if coverage_percentage_has_changed else 0
    sys.exit(exit_code)


def update_coverage_shield(coverage_percentage: int | str) -> bool:
    markdown_line_start = "![Coverage]("
    badge_url = (
        f"https://img.shields.io/badge/Coverage-{coverage_percentage}%25-brightgreen"
    )
    markdown_line = f"{markdown_line_start}{badge_url})"
    current_markdown_lines = Path.readme.lines
    converage_percentage_has_changed = markdown_line not in current_markdown_lines
    lines = (
        markdown_line if line.startswith(markdown_line_start) else line
        for line in current_markdown_lines
    )
    lines_with_empty_lines = *lines, ""
    Path.readme.text = "\n".join(lines_with_empty_lines)
    return converage_percentage_has_changed


def verify_all_files_tested() -> None:
    project_folder = Path.cwd()
    python_files = project_folder.rglob("*.py")
    relative_python_files = {
        str(path.relative_to(project_folder)) for path in python_files
    }
    coverage_lines = cli.lines("coverage report")
    covered_files = set(line.split()[0] for line in coverage_lines[2:-2])
    not_covered_files = relative_python_files - covered_files
    if not_covered_files:
        message_parts = (
            "The following files are not covered by tests:",
            *not_covered_files,
        )
        message = "\n\t".join(message_parts)
        raise Exception(message)

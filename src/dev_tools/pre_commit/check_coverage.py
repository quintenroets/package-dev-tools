import sys
from collections.abc import Iterator

import cli

from dev_tools.utils.package import extract_package_slug

from ..models import Path


def check_coverage(verify_all_files_tested: bool = True) -> None:
    ensure_source_code_used()
    if verify_all_files_tested:
        verify_all_python_files_tested()

    coverage_percentage = cli.get("coverage report --format total")
    coverage_percentage_has_changed = update_coverage_shield(coverage_percentage)
    if coverage_percentage_has_changed:
        print(f"Updated test coverage: {coverage_percentage}%")
        cli.get("coverage html")
    exit_code = 1 if coverage_percentage_has_changed else 0
    sys.exit(exit_code)


def update_coverage_shield(coverage_percentage: float | str) -> bool:
    if isinstance(coverage_percentage, str):
        coverage_percentage = float(coverage_percentage)
    coverage_percentage_int = round(coverage_percentage)
    markdown_line_start = "![Coverage]("
    badge_url_root = "https://img.shields.io/badge"
    badge_url = f"{badge_url_root}/Coverage-{coverage_percentage_int }%25-brightgreen"
    markdown_line = f"{markdown_line_start}{badge_url})"
    current_markdown_lines = Path.readme.lines
    no_badge = not any(markdown_line_start in line for line in current_markdown_lines)
    if no_badge:
        raise Exception("README has no coverage badge yet.")
    converage_percentage_has_changed = markdown_line not in current_markdown_lines
    lines = (
        markdown_line if line.startswith(markdown_line_start) else line
        for line in current_markdown_lines
    )
    lines_with_empty_lines = *lines, ""
    Path.readme.text = "\n".join(lines_with_empty_lines)
    return converage_percentage_has_changed


def verify_all_python_files_tested() -> None:
    python_files = set(generate_python_files())
    coverage_lines = cli.lines("coverage report")
    covered_files = set(line.split()[0] for line in coverage_lines[2:-2])
    not_covered_files = python_files - covered_files
    if not_covered_files:
        message_parts = (
            "The following files are not covered by tests:",
            *not_covered_files,
        )
        message = "\n\t".join(message_parts)
        raise Exception(message)


def generate_python_files() -> Iterator[str]:
    project_folder = Path.cwd()
    python_files = project_folder.rglob("*.py")
    for path in python_files:
        relative_path = path.relative_to(project_folder)
        if relative_path.parts[0] != "build":
            yield str(relative_path)


def ensure_source_code_used():
    package_slug = extract_package_slug()
    is_installed = cli.is_success("pip show", package_slug)
    if is_installed:
        cli.run("pip uninstall -y", package_slug)
        cli.run("coverage run")

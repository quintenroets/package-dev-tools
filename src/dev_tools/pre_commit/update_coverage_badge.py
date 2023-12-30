from ..models import Path


def update_coverage_badge(coverage_percentage: int) -> None:
    markdown_line_start = "![Coverage]("
    badge_url = (
        f"https://img.shields.io/badge/Coverage-{coverage_percentage}%25-brightgreen"
    )
    markdown_line = f"{markdown_line_start}{badge_url})"
    lines = [
        markdown_line if line.startswith(markdown_line_start) else line
        for line in Path.readme.lines
    ]
    lines_with_empty_lines = *lines, ""
    Path.readme.text = "\n".join(lines_with_empty_lines)

import pytest

from package_dev_tools.models import Path
from package_dev_tools.utils.badge import Badge, BadgeUpdater


def test_badge() -> None:
    badge = Badge("Python version", "python-3.10+")
    expected_line = (
        "![Python version](https://img.shields.io/badge/python-3.10+-brightgreen)"
    )
    assert badge.line == expected_line


@pytest.mark.usefixtures("repository_path")
def test_readme_content_preserved() -> None:
    badge = create_python_version_badge(9)
    new_badge = create_python_version_badge(100)
    BadgeUpdater(badge).run()
    readme = Path.readme.text
    BadgeUpdater(new_badge).run()
    assert Path.readme.text == readme.replace(badge.line, new_badge.line)


def create_python_version_badge(version: int) -> Badge:
    return Badge("Python version", f"python-{version}")

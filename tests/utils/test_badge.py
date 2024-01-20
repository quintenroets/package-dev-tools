from package_dev_tools.utils.badge import Badge


def test_badge() -> None:
    badge = Badge("Python version", "python-3.10+")
    expected_line = (
        "![Python version](https://img.shields.io/badge/python-3.10+-brightgreen)"
    )
    assert badge.line == expected_line

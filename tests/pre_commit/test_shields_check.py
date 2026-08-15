import pytest

from package_dev_tools.pre_commit.check_shields import describe_python_versions
from package_dev_tools.utils.python_versions import PythonVersions


@pytest.mark.parametrize(
    ("requirement", "expected"),
    [
        (">=3.11", "3.11+"),
        ("~=3.11", "3.11+"),
        (">=3.13, <4", "3.13+"),
        ("==3.11.*", "3.11"),
        ("~=3.11.0", "3.11"),
        (">=3.11, <3.14", "3.11--3.13"),
        (">=3.11, <=3.13", "3.11--3.13"),
        (">=3.11, !=3.12.1, <3.14", "3.11--3.13"),
        (">3.10, !=3.12.*, <3.14", "3.11%20%7c%203.13"),
        (">=3.12, !=3.13", "3.12%20%7c%203.14"),
    ],
)
def test_describe_python_versions(requirement: str, expected: str) -> None:
    assert describe_python_versions(PythonVersions(requirement)) == expected

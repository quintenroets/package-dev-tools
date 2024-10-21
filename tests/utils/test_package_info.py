import pytest
from typing import Iterator

from package_dev_tools.models import Path
from package_dev_tools.utils.package import PackageInfo

required_python_version = "3.10"
supported_python_versions = ["3.10", "3.11", "3.12", "3.13"]


@pytest.fixture
def package_info(repository_path: Path) -> PackageInfo:
    return PackageInfo(repository_path)


@pytest.fixture
def package_info_with_max_version(repository_path: Path) -> Iterator[PackageInfo]:
    name = "pyproject.toml"
    with Path.tempdir() as directory:
        old = 'requires-python = ">=3.10"'
        new = 'requires-python = ">=3.10, <3.13"'
        path = directory / name
        path.text = (repository_path / name).text.replace(old, new)
        yield PackageInfo(directory)


def test_package_name(package_info: PackageInfo) -> None:
    assert package_info.package_name == "python_package_template"


def test_package_slug(package_info: PackageInfo) -> None:
    assert package_info.package_slug == "python-package-qtemplate"


def test_required_python_version(package_info: PackageInfo) -> None:
    assert package_info.required_python_version == required_python_version


def test_supported_python_versions(package_info: PackageInfo) -> None:
    assert list(package_info.supported_python_versions) == supported_python_versions


def test_supported_python_versions_with_max_version(
    package_info_with_max_version: PackageInfo,
) -> None:
    assert (
        list(package_info_with_max_version.supported_python_versions)
        == supported_python_versions[:-1]
    )


def test_supported_operating_systems(package_info: PackageInfo) -> None:
    expected_operating_systems = {"linux", "macOS", "windows"}
    assert set(package_info.supported_operating_systems) == expected_operating_systems

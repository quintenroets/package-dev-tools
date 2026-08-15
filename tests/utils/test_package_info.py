import pytest

from package_dev_tools.models import Path
from package_dev_tools.utils.package import PackageInfo


@pytest.fixture
def package_info(repository_path: Path) -> PackageInfo:
    return PackageInfo(repository_path)


def test_package_name(package_info: PackageInfo) -> None:
    assert package_info.package_name == "python_package_template"


def test_package_slug(package_info: PackageInfo) -> None:
    assert package_info.package_slug == "python-package-qtemplate"


def test_supported_operating_systems(package_info: PackageInfo) -> None:
    expected_operating_systems = {"linux", "macOS", "windows"}
    assert set(package_info.supported_operating_systems) == expected_operating_systems

from package_dev_tools.models import Path
from package_dev_tools.utils.package import extract_package_name, extract_package_slug


def test_extract_package_name(repository_path: Path):
    package_name = extract_package_name(repository_path)
    assert package_name == "python_package_template"


def test_extract_package_slug(repository_path: Path):
    package_slug = extract_package_slug(repository_path)
    assert package_slug == "python-package-qtemplate"

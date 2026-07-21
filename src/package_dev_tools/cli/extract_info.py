import json

import cli
from package_utils.cli import create_entry_point

from package_dev_tools.utils.package import PackageInfo


def extract_package_name(info: PackageInfo) -> None:
    cli.console.print(info.package_name)


def extract_required_python_version(info: PackageInfo) -> None:
    cli.console.print(info.required_python_version)


def extract_supported_python_versions(info: PackageInfo) -> None:
    cli.console.print(json.dumps(list(info.supported_python_versions)))


package_name = create_entry_point(extract_package_name)
required_python_version = create_entry_point(extract_required_python_version)
supported_python_versions = create_entry_point(extract_supported_python_versions)

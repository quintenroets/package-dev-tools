import json

import cli
from package_utils.cli import instantiate_from_cli_args

from package_dev_tools.utils.package import PackageInfo


def entry_point() -> None:
    package_info = instantiate_from_cli_args(PackageInfo)
    versions = list(package_info.supported_python_versions)
    versions_json = json.dumps(versions)
    cli.console.print(versions_json)

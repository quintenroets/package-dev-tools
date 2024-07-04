import cli
from package_utils.cli import instantiate_from_cli_args

from package_dev_tools.utils.package import PackageInfo


def entry_point() -> None:
    package_info = instantiate_from_cli_args(PackageInfo)
    cli.console.print(package_info.package_name)

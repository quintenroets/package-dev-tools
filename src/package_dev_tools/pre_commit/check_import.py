import importlib

from package_utils.cli import create_entry_point, instantiate_from_cli_args

from package_dev_tools.utils.package import PackageInfo


def check_import() -> None:
    package_info = instantiate_from_cli_args(PackageInfo)
    importlib.import_module(package_info.package_name)


entry_point = create_entry_point(check_import)

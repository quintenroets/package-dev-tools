import importlib

from package_utils.cli import create_entry_point

from package_dev_tools.utils.package import PackageInfo


def check_import(package_info: PackageInfo) -> None:
    importlib.import_module(package_info.package_name)


entry_point = create_entry_point(check_import)

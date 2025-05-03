from package_utils.cli import create_entry_point

from package_dev_tools.pre_commit.export_config import export_config

entry_point = create_entry_point(export_config)

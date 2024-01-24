from package_utils.cli import create_entry_point

from package_dev_tools.pre_commit.check_coverage import check_coverage

entry_point = create_entry_point(check_coverage)

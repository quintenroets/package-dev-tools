from package_utils.cli import create_entry_point

from package_dev_tools.actions.instantiate_new_project.cleanup_readme import (
    ReadmeCleaner,
)

entry_point = create_entry_point(ReadmeCleaner.run, ReadmeCleaner)

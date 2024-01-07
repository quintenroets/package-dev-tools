from package_utils.cli_entry_point import CliEntryPoint

from package_dev_tools.actions.instantiate_new_project.cleanup_readme import (
    ReadmeCleaner,
)


def entry_point() -> None:
    CliEntryPoint(ReadmeCleaner).run()

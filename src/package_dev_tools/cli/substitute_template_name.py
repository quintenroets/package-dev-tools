from package_utils.cli_entry_point import CliEntryPoint

from package_dev_tools.actions.instantiate_new_project.substitute_template_name import (
    NameSubstitutor,
)


def entry_point() -> None:
    CliEntryPoint(NameSubstitutor).run()

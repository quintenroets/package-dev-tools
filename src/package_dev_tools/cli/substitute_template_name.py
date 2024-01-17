from package_utils.cli import create_entry_point

from package_dev_tools.actions.instantiate_new_project.substitute_template_name import (
    NameSubstitutor,
)

entry_point = create_entry_point(NameSubstitutor.run, NameSubstitutor)

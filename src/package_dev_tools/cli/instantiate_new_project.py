from package_utils.cli import create_entry_point

from package_dev_tools.actions.instantiate_new_project import ProjectInstantiator

entry_point = create_entry_point(ProjectInstantiator.run, ProjectInstantiator)

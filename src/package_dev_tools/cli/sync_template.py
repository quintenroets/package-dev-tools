from package_utils.cli import create_entry_point

from package_dev_tools.actions.template_sync.sync import TemplateSyncer

entry_point = create_entry_point(TemplateSyncer.run, TemplateSyncer)

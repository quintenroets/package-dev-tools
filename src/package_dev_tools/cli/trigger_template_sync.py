from package_utils.cli import create_entry_point

from package_dev_tools.actions.trigger_template_sync import TemplateSyncTriggerer

entry_point = create_entry_point(TemplateSyncTriggerer.run, TemplateSyncTriggerer)

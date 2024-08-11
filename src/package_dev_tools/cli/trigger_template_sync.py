from package_utils.cli import create_entry_point

from package_dev_tools.actions.template_sync.trigger import TemplateSyncTriggerer

entry_point = create_entry_point(TemplateSyncTriggerer.run, TemplateSyncTriggerer)

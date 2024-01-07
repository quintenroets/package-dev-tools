from package_utils.cli_entry_point import CliEntryPoint

from package_dev_tools.actions.trigger_template_sync import TemplateSyncTriggerer


def entry_point() -> None:
    CliEntryPoint(TemplateSyncTriggerer).run()

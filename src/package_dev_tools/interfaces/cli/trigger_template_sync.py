import typer

from package_dev_tools.actions.trigger_template_sync import trigger_template_sync


def entry_point() -> None:
    typer.run(trigger_template_sync)

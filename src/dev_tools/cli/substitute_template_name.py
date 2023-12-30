import typer

from dev_tools.actions.substitute_template_name import substitute_template_name


def entry_point() -> None:
    typer.run(substitute_template_name)

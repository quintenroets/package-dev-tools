import typer

from dev_tools.actions.cleanup_readme import cleanup_readme


def entry_point() -> None:
    typer.run(cleanup_readme)

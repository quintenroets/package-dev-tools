import typer

from dev_tools.actions.trigger_template_sync import main


def entry_point() -> None:
    typer.run(main)


if __name__ == "__main__":
    entry_point()

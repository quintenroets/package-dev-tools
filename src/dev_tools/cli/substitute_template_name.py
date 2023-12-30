import typer

from dev_tools.actions.substitute_template_name import main


def entry_point() -> None:
    typer.run(main)


if __name__ == "__main__":
    entry_point()

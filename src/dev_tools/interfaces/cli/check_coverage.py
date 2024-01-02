import typer

from dev_tools.pre_commit.check_coverage import check_coverage


def entry_point() -> None:
    typer.run(check_coverage)

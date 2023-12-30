import typer

from dev_tools.pre_commit.update_coverage_badge import update_coverage_badge


def entry_point() -> None:
    typer.run(update_coverage_badge)

from package_dev_utils.tests.args import no_cli_args
from package_dev_tools import cli


@no_cli_args
def test_entry_point() -> None:
    cli.entry_point()

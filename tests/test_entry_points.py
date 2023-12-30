import pytest
from _pytest.monkeypatch import MonkeyPatch
from dev_tools.cli import update_coverage_badge
from dev_tools.utils import set_cli_args


def test_update_coverage_badge(restore_readme: None, monkeypatch: MonkeyPatch) -> None:
    set_cli_args(monkeypatch, 0)
    with pytest.raises(SystemExit) as exception:
        update_coverage_badge.entry_point()
    assert exception.value.code == 0

import sys
from typing import Any

from _pytest.monkeypatch import MonkeyPatch


def clear_cli_args(monkeypatch: MonkeyPatch) -> None:
    set_cli_args(monkeypatch)


def set_cli_args(monkeypatch: MonkeyPatch, *args: Any) -> None:
    str_args = (str(arg) for arg in args)
    sys_args = ["test_create_instance", *str_args]
    monkeypatch.setattr(sys, "argv", sys_args)

import sys
from pathlib import Path
from unittest.mock import patch

import libcst as cst
import pytest

from package_dev_tools.pre_commit.expand_docstrings import (
    DocstringExpander,
    expand_docstrings,
    expand_file,
)

SINGLE_LINE = 'def foo():\n    """One liner."""\n    pass\n'
EXPANDED = 'def foo():\n    """\n    One liner.\n    """\n    pass\n'
CLASS_SOURCE = 'class Foo:\n    """One liner."""\n    pass\n'


def transform(source: str) -> str:
    module = cst.parse_module(source)
    return module.visit(DocstringExpander(module.default_indent)).code


def test_expands_function_docstring() -> None:
    assert transform(SINGLE_LINE) == EXPANDED


def test_expands_class_docstring() -> None:
    assert '"""\n' in transform(CLASS_SOURCE)


def test_leaves_non_docstring_unchanged() -> None:
    source = "x = 1\n"
    assert transform(source) == source


def test_expand_file_returns_true_when_changed(tmp_path: Path) -> None:
    file = tmp_path / "test.py"
    file.write_text(SINGLE_LINE)
    assert expand_file(file)
    assert file.read_text() == EXPANDED


def test_expand_file_returns_false_when_unchanged(tmp_path: Path) -> None:
    file = tmp_path / "test.py"
    file.write_text(EXPANDED)
    assert not expand_file(file)


def test_expand_docstrings_exits_zero_when_unchanged(tmp_path: Path) -> None:
    file = tmp_path / "test.py"
    file.write_text(EXPANDED)
    with (
        patch.object(sys, "argv", ["prog", str(file)]),
        pytest.raises(SystemExit) as exc,
    ):
        expand_docstrings()
    assert exc.value.code == 0


def test_expand_docstrings_exits_one_when_changed(tmp_path: Path) -> None:
    file = tmp_path / "test.py"
    file.write_text(SINGLE_LINE)
    with (
        patch.object(sys, "argv", ["prog", str(file)]),
        pytest.raises(SystemExit) as exc,
    ):
        expand_docstrings()
    assert exc.value.code == 1

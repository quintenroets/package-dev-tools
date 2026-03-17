import sys
from pathlib import Path
from typing import cast

import libcst as cst

TRIPLE_QUOTE = '"""'


class DocstringExpander(cst.CSTTransformer):
    def __init__(self, default_indent: str) -> None:
        super().__init__()
        self.default_indent = default_indent
        self.indent_stack: list[str] = [""]
        self.expect_docstring_stack: list[bool] = [True]
        self.next_block_eligible: bool = False

    def visit_FunctionDef(self, _node: cst.FunctionDef) -> None:
        self.next_block_eligible = True

    def visit_ClassDef(self, _node: cst.ClassDef) -> None:
        self.next_block_eligible = True

    def visit_IndentedBlock(self, node: cst.IndentedBlock) -> None:
        block_indent = (
            node.indent if isinstance(node.indent, str) else self.default_indent
        )
        self.indent_stack.append(self.indent_stack[-1] + block_indent)
        self.expect_docstring_stack.append(self.next_block_eligible)
        self.next_block_eligible = False

    def leave_IndentedBlock(
        self,
        _original: cst.IndentedBlock,
        updated: cst.IndentedBlock,
    ) -> cst.IndentedBlock:
        self.indent_stack.pop()
        self.expect_docstring_stack.pop()
        return updated

    def leave_SimpleStatementLine(
        self,
        _original: cst.SimpleStatementLine,
        updated: cst.SimpleStatementLine,
    ) -> cst.BaseStatement:
        was_eligible = self.expect_docstring_stack[-1]
        self.expect_docstring_stack[-1] = False
        return (
            self.expand(updated)
            if was_eligible and self.is_one_liner(updated)
            else updated
        )

    def is_one_liner(self, node: cst.SimpleStatementLine) -> bool:
        return (
            len(node.body) == 1
            and isinstance(node.body[0], cst.Expr)
            and isinstance(node.body[0].value, cst.SimpleString)
            and self.is_single_line_triple_quoted(node.body[0].value.value)
        )

    def is_single_line_triple_quoted(self, value: str) -> bool:
        return (
            value.startswith(TRIPLE_QUOTE)
            and value.endswith(TRIPLE_QUOTE)
            and "\n" not in value
            and len(value) > len(TRIPLE_QUOTE) * 2
        )

    def expand(self, node: cst.SimpleStatementLine) -> cst.SimpleStatementLine:
        expr = cast("cst.Expr", node.body[0])
        string = cast("cst.SimpleString", expr.value)
        indent = self.indent_stack[-1]
        quote_len = len(TRIPLE_QUOTE)
        new_string = string.with_changes(
            value=f"{TRIPLE_QUOTE}\n{indent}{string.value[quote_len:-quote_len]}\n{indent}{TRIPLE_QUOTE}",
        )
        return node.with_changes(body=[expr.with_changes(value=new_string)])


def expand_file(path: Path) -> bool:
    source = path.read_text()
    module = cst.parse_module(source)
    updated = module.visit(DocstringExpander(module.default_indent))
    changed = updated.code != source
    if changed:
        path.write_text(updated.code)
    return changed


def expand_docstrings() -> None:
    changed = any(expand_file(Path(p)) for p in sys.argv[1:])
    sys.exit(1 if changed else 0)


entry_point = expand_docstrings

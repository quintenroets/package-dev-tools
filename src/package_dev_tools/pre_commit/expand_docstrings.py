import sys
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import libcst as cst

TRIPLE_QUOTE = '"""'


def is_single_line_triple_quoted(value: str) -> bool:
    return (
        value.startswith(TRIPLE_QUOTE)
        and value.endswith(TRIPLE_QUOTE)
        and "\n" not in value
        and len(value) > len(TRIPLE_QUOTE) * 2
    )


def is_one_liner(node: cst.SimpleStatementLine) -> bool:
    return (
        len(node.body) == 1
        and isinstance(node.body[0], cst.Expr)
        and isinstance(node.body[0].value, cst.SimpleString)
        and is_single_line_triple_quoted(node.body[0].value.value)
    )


@dataclass
class BlockFrame:
    indent: str
    expect_docstring: bool


class DocstringExpander(cst.CSTTransformer):
    def __init__(self, default_indent: str) -> None:
        super().__init__()
        self.default_indent = default_indent
        self.stack: list[BlockFrame] = [BlockFrame("", expect_docstring=True)]
        self.next_block_eligible: bool = False

    def on_visit(self, node: cst.CSTNode) -> bool:
        if isinstance(node, (cst.FunctionDef, cst.ClassDef)):
            self.next_block_eligible = True
        return super().on_visit(node)

    def visit_IndentedBlock(self, node: cst.IndentedBlock) -> None:
        block_indent = (
            node.indent if isinstance(node.indent, str) else self.default_indent
        )
        indent = self.stack[-1].indent + block_indent
        frame = BlockFrame(indent, self.next_block_eligible)
        self.stack.append(frame)
        self.next_block_eligible = False

    def leave_IndentedBlock(
        self,
        _original: cst.IndentedBlock,
        updated: cst.IndentedBlock,
    ) -> cst.IndentedBlock:
        self.stack.pop()
        return updated

    def leave_SimpleStatementLine(
        self,
        _original: cst.SimpleStatementLine,
        updated: cst.SimpleStatementLine,
    ) -> cst.BaseStatement:
        was_eligible = self.stack[-1].expect_docstring
        self.stack[-1].expect_docstring = False
        should_expand = was_eligible and is_one_liner(updated)
        return self.expand(updated) if should_expand else updated

    def expand(self, node: cst.SimpleStatementLine) -> cst.SimpleStatementLine:
        expr = cast("cst.Expr", node.body[0])
        string = cast("cst.SimpleString", expr.value)
        indent = self.stack[-1].indent
        quote_length = len(TRIPLE_QUOTE)
        content = string.value[quote_length:-quote_length]
        new_lines = TRIPLE_QUOTE, f"{indent}{content}", f"{indent}{TRIPLE_QUOTE}"
        new_string = string.with_changes(value="\n".join(new_lines))
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

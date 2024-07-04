from dataclasses import dataclass, field
from functools import cached_property
from typing import ClassVar

from package_dev_tools.models import Path


@dataclass
class Badge:
    title: str
    content: str
    base_url: ClassVar[str] = "https://img.shields.io/badge"
    color: str = "brightgreen"

    @cached_property
    def line_start(self) -> str:
        return f"![{self.title}]"

    @cached_property
    def line(self) -> str:
        url = f"{self.base_url}/{self.content}-{self.color}"
        return f"{self.line_start}({url})"


@dataclass
class BadgeUpdater:
    badge: Badge
    cwd: Path = field(default_factory=Path.cwd)

    def run(self) -> bool:
        path = self.cwd / Path.readme.name
        lines = path.lines
        if not self.contains_badge(lines):
            message = f"README has no {self.badge.title} badge yet."
            raise ValueError(message)
        has_changed = self.badge.line not in lines
        if has_changed:
            lines = (self.badge.line if self.is_badge(line) else line for line in lines)
            path.lines = *lines, ""
        return has_changed

    def contains_badge(self, lines: list[str]) -> bool:
        return any(self.is_badge(line) for line in lines)

    def is_badge(self, line: str) -> bool:
        return line.startswith(self.badge.line_start)

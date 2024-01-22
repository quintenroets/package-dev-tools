from __future__ import annotations

from typing import TypeVar

import plib
from simple_classproperty import classproperty

T = TypeVar("T", bound="Path")


class Path(plib.Path):
    @classproperty
    def readme(cls: type[T]) -> T:  # type: ignore
        return cls("README.md")

    @classproperty
    def workflows(cls: type[T]) -> T:  # type: ignore
        return cls(".github") / "workflows"

    @property
    def has_text_content(self) -> bool:
        try:
            self.text
            has_text = True
        except UnicodeDecodeError:
            has_text = False
        return has_text

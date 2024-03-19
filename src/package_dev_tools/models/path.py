from typing import TypeVar

import superpathlib
from simple_classproperty import classproperty

T = TypeVar("T", bound="Path")


class Path(superpathlib.Path):
    @property
    def has_text_content(self) -> bool:
        try:
            self.text
            has_text = True
        except UnicodeDecodeError:
            has_text = False
        return has_text

    @classmethod
    @classproperty
    def readme(cls: type[T]) -> T:
        return cls("README.md")

    @classmethod
    @classproperty
    def workflows(cls: type[T]) -> T:
        return cls(".github") / "workflows"

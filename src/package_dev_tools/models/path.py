from typing import TypeVar

import superpathlib
from simple_classproperty import classproperty
from typing_extensions import Self

T = TypeVar("T", bound="Path")


class Path(superpathlib.Path):
    @property
    def has_text_content(self) -> bool:
        try:
            self.text  # noqa: B018
            has_text = True
        except UnicodeDecodeError:
            has_text = False
        return has_text

    @classmethod
    @classproperty
    def readme(cls) -> Self:
        return cls("README.md")

    @classmethod
    @classproperty
    def workflows(cls) -> Self:
        return cls(".github") / "workflows"

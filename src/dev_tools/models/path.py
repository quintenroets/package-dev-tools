from __future__ import annotations

from typing import TypeVar

import plib
from simple_classproperty import classproperty

T = TypeVar("T", bound="Path")


class Path(plib.Path):  # type: ignore # TODO: remove after superpathlib fix
    @classproperty
    def readme(cls: type[T]) -> T:
        return cls("README.md")

    @classproperty
    def root(cls: type[T]) -> T:
        return cls(__file__).parent.parent  # type:ignore

    @classproperty
    def repository_root(cls: type[T]) -> T:
        return cls.root.parent.parent  # type: ignore

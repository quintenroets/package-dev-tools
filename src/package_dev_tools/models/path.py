from typing import TypeVar

import superpathlib
from simple_classproperty import classproperty
from typing_extensions import Self

T = TypeVar("T", bound="Path")


class Path(superpathlib.Path):
<<<<<<< HEAD
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
    def readme(cls: type[T]) -> T:
        return cls("README.md")

    @classmethod
    @classproperty
    def workflows(cls: type[T]) -> T:
        return cls(".github") / "workflows"
=======
    @classmethod
    @classproperty
    def source_root(cls) -> Self:
        return cls(__file__).parent.parent

    @classmethod
    @classproperty
    def assets(cls) -> Self:
        path = cls.script_assets / cls.source_root.name
        return cast("Self", path)

    @classmethod
    @classproperty
    def config(cls) -> Self:
        path = cls.assets / "config" / "config.yaml"
        return cast("Self", path)
>>>>>>> template

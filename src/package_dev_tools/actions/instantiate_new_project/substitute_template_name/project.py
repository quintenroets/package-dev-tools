from dataclasses import dataclass, field

from slugify import slugify

from package_dev_tools.models import Path


@dataclass
class Project:
    package_slug: str
    path: Path = field(default_factory=Path.cwd)

    def __post_init__(self) -> None:
        self.check_package_slug()
        self.package_name = slugify(self.package_slug, separator="_")
        self.name = slugify(self.package_slug, separator=" ").title()

    def check_package_slug(self) -> None:
        is_valid = self.package_slug == slugify(self.package_slug) and self.package_slug
        if not is_valid:
            self.raise_invalid_naming_exception()

    def raise_invalid_naming_exception(self) -> None:
        suggested_name = slugify(self.package_slug)
        message = (
            f"The project name '{self.package_slug}' is invalid.\n"
            f"Suggested name: {suggested_name}"
        )
        raise ValueError(message)

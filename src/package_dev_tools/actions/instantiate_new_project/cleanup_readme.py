from dataclasses import dataclass, field

from package_dev_tools.models import Path


@dataclass
class ReadmeCleaner:
    """
    Remove documentation that is irrelevant for derived projects.
    """

    path: Path = field(default_factory=Path.cwd)
    delimiter: str = "#" * 6 + " " + "=" * 60
    keyword: str = "## Usage\n"

    def run(self) -> None:
        path = self.path / Path.readme
        if self.delimiter in path.text:
            text_parts = path.text.split(self.delimiter)
            text_parts[0] = text_parts[0].split(self.keyword)[0]
            path.text = self.keyword.join(text_parts)

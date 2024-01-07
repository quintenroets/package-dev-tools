from dataclasses import dataclass, field

from ...models import Path


@dataclass
class ReadmeCleaner:
    """
    Remove documentation that is irrelevant for derived projects.
    """

    path: Path = field(default_factory=Path.cwd)
    delimiter: str = "=" * 60 + "\n"
    keyword: str = "## Usage"

    def run(self):
        path = self.path / Path.readme
        text_parts = path.text.split(self.delimiter)
        text_parts[0] = text_parts[0].split(self.keyword)[0]
        path.text = self.keyword.join(text_parts)

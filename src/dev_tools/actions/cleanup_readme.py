from ..models import Path


def cleanup_readme() -> None:
    path = Path.readme
    delimiter = "=" * 60 + "\n"
    keyword = "## Usage"
    text_parts = path.text.split(delimiter)
    text_parts[0] = text_parts[0].split(keyword)[0]
    path.text = keyword.join(text_parts)

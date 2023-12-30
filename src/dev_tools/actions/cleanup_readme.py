from plib import Path


def main() -> None:
    path = Path("README.md")
    delimiter = "=" * 60 + "\n"
    keyword = "## Usage"
    text_parts = path.text.split(delimiter)
    text_parts[0] = text_parts[0].split(keyword)[0]
    path.text = keyword.join(text_parts)

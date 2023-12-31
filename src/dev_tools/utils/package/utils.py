import tomllib
import urllib.parse
from typing import Any

from ...models import Path


def extract_package_name(path: Path = None) -> str:
    info = extract_pyproject_info(path)
    package_data = info["tool"]["setuptools"]["package-data"]
    project_name = next(iter(package_data))
    return project_name


def extract_package_slug(path: Path = None) -> str:
    info = extract_pyproject_info(path)
    project_urls = info["project"]["urls"].values()
    project_url: str = next(iter(project_urls))
    parsed_url = urllib.parse.urlparse(project_url)
    return parsed_url.path.split("/")[-1]


def extract_pyproject_info(path: Path) -> dict[str, Any]:
    if path is None:
        path = Path.cwd()
    info_path = path / "pyproject.toml"
    return tomllib.loads(info_path.text)

from typing import Any

import toml
from plib import Path


def extract_package_name(path: Path | None = None) -> str:
    info = extract_pyproject_info(path)
    package_data = info["tool"]["setuptools"]["package-data"]
    project_name = next(iter(package_data))
    return project_name


def extract_package_slug(path: Path | None = None) -> str:
    info = extract_pyproject_info(path)
    return info["project"]["name"]


def extract_pyproject_info(path: Path | None) -> dict[str, Any]:
    if path is None:
        path = Path.cwd()
    info_path = path / "pyproject.toml"
    return toml.loads(info_path.text)

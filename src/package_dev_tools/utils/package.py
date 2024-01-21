import typing
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any, ClassVar

import requests
import toml
from plib import Path


@dataclass
class PackageInfo:
    path: Path = field(default_factory=Path.cwd)
    os_mapper: ClassVar[dict[str, str]] = {"ubuntu": "linux", "macos": "macOS"}

    @property
    def package_name(self) -> str:
        package_data = self.pyproject_info["tool"]["setuptools"]["package-data"]
        project_name = next(iter(package_data))
        return typing.cast(str, project_name)

    @property
    def package_slug(self) -> str:
        package_slug = self.pyproject_info["project"]["name"]
        return typing.cast(str, package_slug)

    @property
    def required_python_version(self) -> str:
        version = self.pyproject_info["project"]["requires-python"].split(">=")[1]
        return typing.cast(str, version)

    @property
    def required_python_minor(self) -> int:
        minor_version = self.required_python_version.split(".")[-1]
        return int(minor_version)

    @property
    def supported_python_versions(self) -> Iterator[str]:
        latest_python_minor = self.retrieve_latest_python_minor()
        minors = range(self.required_python_minor, latest_python_minor + 1)
        return (f"3.{minor_version}" for minor_version in minors)

    def retrieve_latest_python_minor(self) -> int:
        minor_version = self.required_python_minor
        while self.release_exists(minor_version + 1):
            minor_version += 1
        return minor_version

    @classmethod
    def release_exists(cls, minor_version: int) -> bool:
        version = f"3.{minor_version}.0"
        base_url = "https://www.python.org/ftp/python/"
        filename = f"Python-{version}.tar.xz"
        url = f"{base_url}/{version}/{filename}"
        return requests.head(url).status_code == 200

    @property
    def pyproject_info(self) -> dict[str, Any]:
        info_path = self.path / "pyproject.toml"
        return toml.loads(info_path.text)

    @property
    def supported_operating_systems(self) -> Iterator[str]:
        workflow_path = self.path / ".github" / "workflows" / "build.yml"
        os_keyword = "os: ["
        os_line = next(line for line in workflow_path.lines if os_keyword in line)
        os_entries = os_line.split(os_keyword)[1].split("]")[0].split(",")
        for entry in os_entries:
            parsed_entry = entry.strip().replace("-latest", "")
            mapped_entry = self.os_mapper.get(parsed_entry, parsed_entry)
            yield mapped_entry

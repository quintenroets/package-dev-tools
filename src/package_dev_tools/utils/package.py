import typing
from collections.abc import Iterator
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, ClassVar

import toml
from superpathlib import Path

from .python_versions import PythonVersions


@dataclass
class PackageInfo:
    path: Path = field(default_factory=Path.cwd)
    os_mapper: ClassVar[dict[str, str]] = {"ubuntu": "linux", "macos": "macOS"}

    @property
    def package_name(self) -> str:
        package_data = self.pyproject_info["tool"]["setuptools"]["package-data"]
        project_name = next(iter(package_data))
        return typing.cast("str", project_name)

    @property
    def package_slug(self) -> str:
        package_slug = self.pyproject_info["project"]["name"]
        return typing.cast("str", package_slug)

    @cached_property
    def python_versions(self) -> PythonVersions:
        requirement = self.pyproject_info["project"]["requires-python"]
        return PythonVersions(typing.cast("str", requirement))

    @cached_property
    def pyproject_info(self) -> dict[str, Any]:
        info_path = self.path / "pyproject.toml"
        return toml.loads(info_path.text)

    @property
    def supported_operating_systems(self) -> Iterator[str]:
        workflow_path = self.path / ".github" / "workflows" / "build.yml"
        workflow = typing.cast("dict[str, Any]", workflow_path.yaml)
        matrices = (
            job.get("strategy", {}).get("matrix", {})
            for job in workflow["jobs"].values()
        )
        entries = next(matrix["os"] for matrix in matrices if "os" in matrix)
        for entry in typing.cast("list[str]", entries):
            operating_system = entry.removesuffix("-latest")
            yield self.os_mapper.get(operating_system, operating_system)

from collections.abc import Iterator
from dataclasses import dataclass
from functools import cache, cached_property
from typing import Any, ClassVar

import requests
from packaging.specifiers import SpecifierSet
from packaging.version import Version


@dataclass
class PythonVersions:
    requirement: str
    major: ClassVar[int] = 3

    @property
    def required(self) -> str:
        return str(min(self.specified_versions))

    @property
    def supported(self) -> list[str]:
        versions = (
            self.specified_versions
            if self.is_bounded
            else self.included_versions(fetch_latest_python_version(self.major))
        )
        return [str(version) for version in versions]

    @property
    def maximum(self) -> str | None:
        return str(max(self.specified_versions)) if self.is_bounded else None

    @property
    def has_excluded_minors(self) -> bool:
        minors = [version.minor for version in self.specified_versions]
        return minors != list(range(min(minors), max(minors) + 1))

    @cached_property
    def specified_versions(self) -> list[Version]:
        return list(self.included_versions(self.search_ceiling))

    @cached_property
    def is_bounded(self) -> bool:
        return self.search_ceiling not in self.specifiers

    @cached_property
    def search_ceiling(self) -> Version:
        versions = (
            Version(specifier.version.removesuffix(".*"))
            for specifier in self.specifiers
        )
        minors = (version.minor for version in versions if version.major == self.major)
        return self.version(max(minors, default=0) + 1)

    def included_versions(self, ceiling: Version) -> Iterator[Version]:
        candidates = (self.version(minor) for minor in range(ceiling.minor + 1))
        return (version for version in candidates if version in self.specifiers)

    @cached_property
    def specifiers(self) -> SpecifierSet:
        return SpecifierSet(self.requirement)

    def version(self, minor: int) -> Version:
        return Version(f"{self.major}.{minor}")


@cache
def fetch_latest_python_version(major: int) -> Version:
    url = "https://www.python.org/api/v2/downloads/release/"
    parameters = {"is_published": "true", "pre_release": "false"}
    response = requests.get(url, params=parameters, timeout=10)
    releases: list[dict[str, Any]] = response.json()
    return max(
        Version(release["name"].removeprefix("Python "))
        for release in releases
        if release["version"] == major
    )

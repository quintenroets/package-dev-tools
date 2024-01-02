from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

import cli
from slugify import slugify

from package_dev_tools.utils.package import extract_package_name, extract_package_slug

from .path import Path
from .project import Project


@dataclass
class NameSubstitutor:
    project_name: str
    path: Path
    current_project_name: str = ""
    custom_template_package_name: str = "python-package-qtemplate"

    def __post_init__(self) -> None:
        self.new_project = Project(self.project_name, self.path)
        if not self.current_project_name:
            self.current_project_name = self.extract_current_project_name()
        self.template_project = Project(self.current_project_name, self.path)
        self.substitutions = {
            self.custom_template_package_name: self.template_project.package_slug,
            self.template_project.name: self.new_project.name,
            self.template_project.package_slug: self.new_project.package_slug,
            self.template_project.package_name: self.new_project.package_name,
        }

    def extract_current_project_name(self) -> str:
        package_slug = extract_package_slug(self.path)
        if package_slug == self.custom_template_package_name:
            package_name = extract_package_name(self.path)
            package_slug = slugify(package_name, separator="-")
        return package_slug

    def run(self) -> None:
        for path in self.generate_paths_to_substitute():
            self.apply_substitutions(path)

    def apply_substitutions(self, path: Path) -> None:
        content = path.text
        if any(to_replace in content for to_replace in self.substitutions):
            for original, replacement in self.substitutions.items():
                content = content.replace(original, replacement)
            path.text = content

    def generate_paths_to_substitute(self) -> Iterator[Path]:
        workflows_folder = self.path / ".github" / "workflows"
        for path in self.generate_project_files():
            # Modifying workflow files requires additional permissions.
            # Therefore, we don't do substitute those
            is_workflow = path.is_relative_to(workflows_folder)
            is_file = path.is_file()
            if not is_workflow and is_file:
                if path.has_text_content:
                    yield path
                self.rename(path)

    def rename(self, path: Path) -> None:
        if any(name == self.template_project.package_name for name in path.parts):
            renamed_path_str = str(path).replace(
                self.template_project.package_name,
                self.new_project.package_name,
            )
            renamed_path = Path(renamed_path_str)
            path.rename(renamed_path)

    def generate_project_files(self) -> Iterator[Path]:
        command = ("git", "ls-tree", "-r", "HEAD", "--name-only")
        relative_paths = cli.lines(command, cwd=self.path)
        for path in relative_paths:
            yield self.path / path


def substitute_template_name(
    project_name: str = "",
    path_str: str = "",
    current_project_name: str = "",
) -> None:
    # TODO: use create instance from cli args from package-utils
    path = Path(path_str) if path_str else Path.cwd()
    NameSubstitutor(project_name, path, current_project_name=current_project_name).run()

import urllib.parse
from collections.abc import Iterator
from dataclasses import dataclass, field

import cli
from slugify import slugify

from package_dev_tools.actions.instantiate_new_project.git import GitInterface
from package_dev_tools.models import Path
from package_dev_tools.utils.package import PackageInfo

from .project import Project


@dataclass
class NameSubstitutor:
    """Rename all references to python-package-template when a new project is created
    from the template repository.

    This includes:
    - python-package-template
    - python_package_template
    - Python Package Template
    The new project name is automatically inferred when not specified.
    """

    project_name: str | None = None
    path: Path = field(default_factory=Path.cwd)
    current_project_name: str | None = None
    custom_template_package_name: str = "python-package-qtemplate"

    def __post_init__(self) -> None:
        if self.project_name is None:
            self.project_name = self.extract_new_project_name()
        if self.current_project_name is None:
            self.current_project_name = self.extract_current_project_name()
        self.new_project = Project(self.project_name, self.path)
        self.template_project = Project(self.current_project_name, self.path)
        self.substitutions = {
            self.custom_template_package_name: self.template_project.package_slug,
            self.template_project.name: self.new_project.name,
            self.template_project.package_slug: self.new_project.package_slug,
            self.template_project.package_name: self.new_project.package_name,
        }

    def extract_new_project_name(self) -> str:
        git_url = GitInterface(self.path).capture_output("config remote.origin.url")
        return urllib.parse.urlparse(git_url).path.split("/")[-1].removesuffix(".git")

    def extract_current_project_name(self) -> str:
        package_info = PackageInfo(self.path)
        package_slug = package_info.package_slug
        if package_slug == self.custom_template_package_name:
            package_name = package_info.package_name
            package_slug = slugify(package_name, separator="-")
        return package_slug

    def run(self) -> None:
        for path in self.generate_paths_to_substitute():
            if path.has_text_content:
                self.substitute_content(path)
            self.substitute_name(path)

    def substitute_content(self, path: Path) -> None:
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
                yield path

    def substitute_name(self, path: Path) -> None:
        if any(name == self.template_project.package_name for name in path.parts):
            renamed_path_str = str(path).replace(
                self.template_project.package_name,
                self.new_project.package_name,
            )
            renamed_path = Path(renamed_path_str)
            path.rename(renamed_path)

    def generate_project_files(self) -> Iterator[Path]:
        command = ("git", "ls-tree", "-r", "HEAD", "--name-only")
        relative_paths = cli.capture_output_lines(command, cwd=self.path)
        for path in relative_paths:
            yield self.path / path

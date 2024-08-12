import shutil
from collections.abc import Iterator
from dataclasses import dataclass
from functools import cached_property

from superpathlib import Path

from package_dev_tools import models
from package_dev_tools.actions.instantiate_new_project import ProjectInstantiator
from package_dev_tools.actions.instantiate_new_project.git import GitInterface


@dataclass
class Merger:  # pragma: nocover
    repository_directory: Path
    template_directory: Path
    repository: str
    template_branch: str = "template"
    show_conflicts: bool = True

    @cached_property
    def git(self) -> GitInterface:
        path = models.Path(self.template_directory)
        git = GitInterface(path)
        git.configure()
        return git

    def merge_in_template_updates(self) -> None:
        self.branch_template_updates()
        self.create_branch_with(self.repository_directory)
        action = "merge" if self.show_conflicts else "merge -X ours"
        self.git.run(f"{action} {self.template_branch} -m 'merge'", check=False)
        self.overwrite_project_files(self.template_directory, self.repository_directory)

    def branch_template_updates(self) -> None:
        with Path.tempfile(create=False) as latest_template_directory:
            shutil.copytree(self.template_directory, latest_template_directory)
            self.git.capture_output("reset --hard HEAD~1")
            self.instantiate(path=latest_template_directory)
            self.instantiate(path=self.template_directory)
            self.create_branch_with(
                latest_template_directory,
                name=self.template_branch,
            )

    def instantiate(self, path: Path) -> None:
        path_with_methods = models.Path(path)
        ProjectInstantiator(project_name=self.repository, path=path_with_methods).run()

    def create_branch_with(self, path: Path, name: str = "branch") -> None:
        self.git.capture_output("checkout main")
        self.git.capture_output("checkout -b", name)
        self.overwrite_project_files(path, self.template_directory)
        self.git.capture_output("add -A")
        self.git.commit()

    def overwrite_project_files(self, source: Path, destination: Path) -> None:
        self.remove_project_files(destination)
        for relative_file in self.generate_project_files():
            file = source / relative_file
            destination_file = destination / relative_file
            file.copy_to(destination_file, include_properties=False)

    def generate_project_files(self) -> Iterator[Path]:
        path = models.Path(self.repository_directory)
        instantiator = ProjectInstantiator(path=path, current_project_name="dummy")
        for file in instantiator.generate_project_files():
            yield file.relative_to(path)

    @classmethod
    def remove_project_files(cls, directory: Path) -> None:
        path = models.Path(directory)
        instantiator = ProjectInstantiator(path=path)
        for file in instantiator.generate_project_files():
            file.unlink()

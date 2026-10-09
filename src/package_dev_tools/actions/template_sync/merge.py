import shutil
from dataclasses import dataclass

from superpathlib import Path

from package_dev_tools import models
from package_dev_tools.actions.instantiate_new_project import ProjectInstantiator
from package_dev_tools.utils import git


@dataclass
class Merger:  # pragma: nocover
    repository_directory: Path
    template_directory: Path
    repository: str
    template_branch: str = "template"
    show_conflicts: bool = True

    def merge_in_template_updates(self) -> None:
        self.branch_template_updates()
        self.create_branch_with(self.repository_directory)
        action = "merge" if self.show_conflicts else "merge -X ours"
        command = f"{action} {self.template_branch} -m merge"
        git.capture_output(self.template_directory, command, check=False)
        self.overwrite_project_files(self.template_directory, self.repository_directory)

    def branch_template_updates(self) -> None:
        with Path.tempfile(create=False) as latest_template_directory:
            shutil.copytree(self.template_directory, latest_template_directory)
            git.capture_output(self.template_directory, "reset --hard HEAD~1")
            self.instantiate(path=latest_template_directory)
            self.instantiate(path=self.template_directory)
            self.create_branch_with(
                latest_template_directory, name=self.template_branch
            )

    def instantiate(self, path: Path) -> None:
        path_with_methods = models.Path(path)
        ProjectInstantiator(project_name=self.repository, path=path_with_methods).run()

    def create_branch_with(self, path: Path, name: str = "branch") -> None:
        git.capture_output(self.template_directory, "checkout -B", name, "main")
        self.overwrite_project_files(path, self.template_directory)
        git.capture_output(self.template_directory, "add -A")
        git.commit(self.template_directory, "Instantiate new project", allow_empty=True)

    def overwrite_project_files(self, source: Path, destination: Path) -> None:
        self.remove_project_files(destination)
        for relative_file in git.generate_relative_files(self.repository_directory):
            file = source / relative_file
            destination_file = destination / relative_file
            destination_file.byte_content = file.byte_content if file.exists() else b""

    @classmethod
    def remove_project_files(cls, directory: Path) -> None:
        for file in git.generate_files(directory):
            file.unlink()

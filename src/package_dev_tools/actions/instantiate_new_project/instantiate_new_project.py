from dataclasses import dataclass

from package_dev_tools.utils.git import GitInterface

from .cleanup_readme import ReadmeCleaner
from .cleanup_workflows import WorkflowsCleaner
from .substitute_template_name import NameSubstitutor


@dataclass
class ProjectInstantiator(NameSubstitutor):
    commit: bool = True

    def run(self) -> None:
        """
        Instantiate new project from template repository.
        """
        runners = (
            super(),
            ReadmeCleaner(self.path),
            WorkflowsCleaner(self.path),
        )
        for runner in runners:
            runner.run()  # type: ignore[union-attr]

        git = GitInterface(self.path)
        git.clean()
        if self.commit:
            git.commit("Instantiate new project")

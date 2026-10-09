from dataclasses import dataclass

from package_dev_tools.utils import git

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
        runners = (super(), ReadmeCleaner(self.path), WorkflowsCleaner(self.path))
        for runner in runners:
            runner.run()  # type: ignore[union-attr]

        git.capture_output(self.path, "add -A")
        git.capture_output(self.path, "clean -fd")
        if self.commit:
            git.commit(self.path, "Instantiate new project")

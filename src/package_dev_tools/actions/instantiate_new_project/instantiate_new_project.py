from dataclasses import dataclass, field

from ...models import Path
from .cleanup_readme import ReadmeCleaner
from .cleanup_workflows import WorkflowsCleaner
from .git import GitInterface
from .substitute_template_name import NameSubstitutor


@dataclass
class ProjectInstantiator:
    project_name: str = ""
    path: Path = field(default_factory=Path.cwd)
    current_project_name: str = ""
    commit: bool = True

    def run(self) -> None:
        """
        Instantiate new project from template repository.
        """
        runners = (
            NameSubstitutor(self.project_name, self.path, self.current_project_name),
            ReadmeCleaner(self.path),
            WorkflowsCleaner(self.path),
        )
        for runner in runners:
            runner.run()  # type: ignore
        if self.commit:
            GitInterface(self.path).commit()

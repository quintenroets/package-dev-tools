from dataclasses import dataclass, field

from package_dev_tools.models import Path


@dataclass
class WorkflowsCleaner:
    path: Path = field(default_factory=Path.cwd)
    template_only_workflows: tuple[str, ...] = (
        "instantiate-new-project.yml",
        "trigger-template-sync.yml",
    )

    def run(self) -> None:
        """Some workflows in the template repository do not need to run in derived
        repositories.

        This action removes them from newly instantiated projects
        derived from the template repository.
        """
        workflows_folder = self.path / Path.workflows
        for name in self.template_only_workflows:
            workflow_file = workflows_folder / name
            workflow_file.unlink(missing_ok=True)

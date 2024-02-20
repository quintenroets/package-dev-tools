from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from github import UnknownObjectException
from github.Repository import Repository

from . import git


@dataclass
class TemplateSyncTriggerer(git.Client):
    workflow_name: str = "sync-template.yml"
    max_workers: int = 10

    def run(self) -> None:
        paginated_repos = self.client.get_user().get_repos(type="owner")
        repos = list(paginated_repos)
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            executor.map(self.trigger_if_possible, repos)

    def trigger_if_possible(self, repo: Repository) -> None:
        try:
            workflow = repo.get_workflow(self.workflow_name)
        except UnknownObjectException:
            workflow = None

        if workflow is not None:
            workflow.create_dispatch("main")

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from github import Github, Repository, UnknownObjectException
from plib import Path


@dataclass
class TemplateSyncTriggerer:
    token: str
    workflow_name: Path = "sync-template.yml"
    max_workers: int = 10

    def __post_init__(self) -> None:
        self.client = Github(self.token)

    def run(self) -> None:
        repos = self.client.get_user().get_repos(type="owner")
        repos = list(repos)
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            executor.map(self.trigger_if_possible, repos)

    def trigger_if_possible(self, repo: Repository) -> None:
        try:
            workflow = repo.get_workflow(self.workflow_name)
        except UnknownObjectException:
            workflow = None

        if workflow is not None:
            workflow.create_dispatch("main")


def main(token: str) -> None:
    TemplateSyncTriggerer(token).run()

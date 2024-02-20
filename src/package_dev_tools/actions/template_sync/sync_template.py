import typing
from dataclasses import dataclass, field
from functools import cached_property

import cli
import github.Auth
from github.Commit import Commit
from github.Repository import Repository
from plib import Path

from ..instantiate_new_project import ProjectInstantiator
from ..instantiate_new_project.git import GitInterface
from ..instantiate_new_project.substitute_template_name import substitute_template_name
from . import git


@dataclass
class TemplateSyncer(git.Client):  # pragma: nocover
    repository: str
    ignore_patterns_path: Path = Path(".templatesyncignore")
    template_repository: str = "quintenroets/python-package-template"
    only_latest_commit: bool = True
    default_branch: str = "main"
    update_branch: str = "sync-template"
    downloaded_repository_folder: Path = field(init=False)
    downloaded_template_repository_folder: Path = field(init=False)

    def run(self) -> None:
        self.downloaded_repository_folder = Path.tempfile(create=False)
        self.downloaded_template_repository_folder = Path.tempfile(create=False)
        paths = (
            self.downloaded_repository_folder,
            self.downloaded_template_repository_folder,
        )
        with paths[0], paths[1]:
            self._run()

    def _run(self) -> None:
        self.clone_repository()
        is_updated = self.apply_updates()
        if is_updated:
            self.push_updates()

    def clone_repository(self) -> None:
        try:
            self.repository_client.get_branch(self.update_branch)
            update_branch_exists = True
        except github.GithubException:
            update_branch_exists = False
        url = self.repository_client.clone_url
        clone = (
            ("clone", "-b", self.update_branch) if update_branch_exists else ("clone",)
        )
        cli.run("git", clone, url, self.downloaded_repository_folder)
        if not update_branch_exists:
            self.run_git("checkout", "-b", self.update_branch)

    def apply_updates(self) -> bool:
        updates = self.extract_template_updates()
        try:
            self.run_git("apply", input_=updates)
            is_updated = True
        except cli.CalledProcessError:
            self.instantiate_template()
            self.pull_template()
            is_updated = self.commit_updated_files()
        return is_updated

    def extract_template_updates(self) -> str:
        if not self.downloaded_template_repository_folder.exists():
            self.clone_template_repository()
        cwd = self.downloaded_template_repository_folder
        result = cli.get("git", "diff", "-U0", "HEAD^", "HEAD", cwd=cwd)
        return typing.cast(str, result)

    def clone_template_repository(self) -> None:
        url = self.template_repository_client.clone_url
        path = self.downloaded_template_repository_folder
        cli.run("git", "clone", url, path)

    def run_git(self, *args: str | Path, input_: str | None = None) -> None:
        cli.run("git", *args, input=input_, cwd=self.downloaded_repository_folder)

    def instantiate_template(self) -> None:
        project_name = self.repository.split("/")[-1]

        path = substitute_template_name.Path(self.downloaded_template_repository_folder)
        instantiator = ProjectInstantiator(project_name=project_name, path=path)
        instantiator.run()

    def pull_template(self) -> None:
        self.run_git("config", "pull.rebase", "false")
        self.configure_git()
        command = (
            "pull",
            self.downloaded_template_repository_folder,
            self.default_branch,
            "--allow-unrelated-histories",
            "--squash",
            "--strategy=recursive",
            "-X",
            "theirs",
        )
        self.run_git(*command)
        self.run_git("status", "-v")

    def commit_updated_files(self) -> bool:
        self.run_git("reset")

        for changed_file in self.latest_commit.files:
            if changed_file.previous_filename:
                self.run_git("add", changed_file.previous_filename)
            self.run_git("add", changed_file.filename)

        if self.ignore_patterns_path.exists():
            self.run_git("reset", f"--pathspec-from-file={self.ignore_patterns_path}")
        self.configure_git()
        try:
            self.run_git(
                "commit", "-m", self.latest_commit.commit.message, "--no-verify"
            )
            is_updated = True
        except cli.CalledProcessError:
            is_updated = False
        return is_updated

    def push_updates(self) -> None:
        self.run_git("push", "--set-upstream", "origin", self.update_branch)
        try:
            self.repository_client.create_pull(
                self.default_branch,
                self.update_branch,
                title="Sync template changes",
                body="",
            )
        except github.GithubException:
            pass  # Pull request already created

    @cached_property
    def repository_client(self) -> Repository:
        return self.client.get_repo(self.repository)

    @cached_property
    def template_repository_client(self) -> Repository:
        return self.client.get_repo(self.template_repository)

    @cached_property
    def latest_commit(self) -> Commit:
        commits = self.template_repository_client.get_commits()
        return next(iter(commits))

    def configure_git(self) -> None:
        path = substitute_template_name.Path(self.downloaded_repository_folder)
        GitInterface(path).configure()

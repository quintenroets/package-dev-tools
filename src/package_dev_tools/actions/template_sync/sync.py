import contextlib
from collections.abc import Iterator
from dataclasses import dataclass, field
from functools import cached_property

import cli
import github.Auth
from github.Commit import Commit
from github.Repository import Repository
from slugify import slugify
from superpathlib import Path

from package_dev_tools import models
from package_dev_tools.actions.instantiate_new_project.git import GitInterface

from . import git
from .merge import Merger


@dataclass
class TemplateSyncer(git.Client):
    repository: str
    ignore_patterns_path: Path = field(
        default_factory=lambda: Path(".templatesyncignore"),
    )
    template_repository: str = "quintenroets/python-package-template"
    default_branch: str = "main"
    update_branch: str = "sync-template"
    show_conflicts: bool = True

    @property
    def project_name(self) -> str:
        return self.extract_name(self.repository)

    @property
    def template_name(self) -> str:
        return self.extract_name(self.template_repository)

    @classmethod
    def extract_name(cls, repository: str) -> str:
        return repository.split("/")[-1]

    def run(self) -> None:
        merger = Merger(
            self.downloaded_repository_directory,
            self.downloaded_template_repository_directory,
            self.project_name,
            show_conflicts=self.show_conflicts,
        )
        with (
            self.downloaded_repository_directory,
            self.downloaded_template_repository_directory,
        ):
            merger.merge_in_template_updates()
            is_updated = self.commit_updated_files()
            if is_updated:
                self.push_updates()

    def run_git(
        self,
        *args: str | Path,
        input_: str | None = None,
        check: bool = True,
    ) -> None:
        cwd = self.downloaded_repository_directory
        cli.run("git", *args, input=input_, cwd=cwd, check=check)

    def commit_updated_files(self) -> bool:
        self.reset_files_not_in_template_commit()
        self.apply_ignore_patterns()
        path = models.Path(self.downloaded_repository_directory)
        try:
            GitInterface(path=path, commit_message=self.commit_message).commit()
            is_updated = True
        except cli.CalledProcessError:
            is_updated = False
        return is_updated

    def reset_files_not_in_template_commit(self) -> None:
        self.run_git("reset")
        files = self.generate_instantiated_files_in_template_commit()
        for file_ in files:
            self.run_git("add", file_, check=False)

    def generate_instantiated_files_in_template_commit(self) -> Iterator[str]:
        package_name = slugify(self.project_name, separator="_")
        template_package_name = slugify(self.template_name, separator="_")
        for file_ in self.generate_files_in_template_commit():
            yield file_.replace(template_package_name, package_name)

    def generate_files_in_template_commit(self) -> Iterator[str]:  # pragma: nocover
        for changed_file in self.latest_commit.files:
            if changed_file.previous_filename is not None:
                yield changed_file.previous_filename
            yield changed_file.filename

    def apply_ignore_patterns(self) -> None:
        path = self.downloaded_repository_directory / self.ignore_patterns_path
        if path.exists():
            for line in path.lines:
                pattern = f"{line}*" if line.endswith("/") else line
                self.run_git("reset", pattern)

    def push_updates(self) -> None:  # pragma: nocover
        self.run_git("push", "--set-upstream", "origin", self.update_branch)
        body = self.create_pull_request_body()
        with contextlib.suppress(
            github.GithubException,  # Pull request already created
        ):
            self.repository_client.create_pull(
                self.default_branch,
                self.update_branch,
                title=self.commit_message,
                body=body,
            )

    def create_pull_request_body(self) -> str:
        pull_request_tokens = "(#"
        if pull_request_tokens in self.latest_commit.commit.message:
            message = self.latest_commit.commit.message
            number = message.split(pull_request_tokens)[-1].split(")")[0]
            name = f"#{number}"
            repository_url = self.template_repository_client.clone_url.removesuffix(
                ".git",
            )
            url = f"{repository_url}/pull/{number}"
        else:
            name = self.latest_commit.commit.sha
            url = self.latest_commit.commit.html_url
        return f"Sync template repository updates in [{name}]({url})"

    @cached_property
    def commit_message(self) -> str:
        return self.latest_commit.commit.message.split("(#")[0]

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

    @cached_property
    def downloaded_repository_directory(self) -> Path:
        path = Path.tempfile(create=False)
        self.clone_repository(path)
        return path

    @cached_property
    def downloaded_template_repository_directory(self) -> Path:
        path = Path.tempfile(create=False)
        self.clone_template_repository(path)
        return path

    def clone_repository(self, path: Path) -> None:  # pragma: nocover
        try:
            self.repository_client.get_branch(self.update_branch)
            update_branch_exists = True
        except github.GithubException:
            update_branch_exists = False
        clone = (
            ("clone", "-b", self.update_branch) if update_branch_exists else ("clone",)
        )
        cli.run("git", clone, self.project_clone_url, path)
        if not update_branch_exists:
            cli.run("git checkout -b", self.update_branch, cwd=path)

    @property
    def project_clone_url(self) -> str:
        url = self.repository_client.clone_url
        prefix = "https://"
        username = self.repository.split("/")[0]
        return url.replace(prefix, f"{prefix}{username}:{self.token}@")

    def clone_template_repository(self, path: Path) -> None:
        url = self.template_repository_client.clone_url
        cli.run("git", "clone", url, path)

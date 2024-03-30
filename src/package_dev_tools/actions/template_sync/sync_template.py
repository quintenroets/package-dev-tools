from collections.abc import Iterator
from dataclasses import dataclass, field
from functools import cached_property

import cli
import github.Auth
from github.Commit import Commit
from github.Repository import Repository
from slugify import slugify
from superpathlib import Path

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
        prefix = "https://"
        username = self.repository.split("/")[0]
        url = url.replace(prefix, f"{prefix}{username}:{self.token}@")
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
        return cli.capture_output("git", "diff", "-U0", "HEAD^", "HEAD", cwd=cwd)

    def clone_template_repository(self) -> None:
        url = self.template_repository_client.clone_url
        path = self.downloaded_template_repository_folder
        cli.run("git", "clone", url, path)

    def run_git(
        self, *args: str | Path, input_: str | None = None, check: bool = True
    ) -> None:
        cwd = self.downloaded_repository_folder
        cli.run("git", *args, input=input_, cwd=cwd, check=check)

    def instantiate_template(self) -> None:
        path = substitute_template_name.Path(self.downloaded_template_repository_folder)
        instantiator = ProjectInstantiator(project_name=self.project_name, path=path)
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

    def commit_updated_files(self) -> bool:
        if self.only_latest_commit:
            self.reset_files_not_in_template_commit()
        self.apply_ignore_patterns()
        self.configure_git()
        command = "commit", "-m", self.latest_commit.commit.message, "--no-verify"
        try:
            self.run_git(*command)
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

    def generate_files_in_template_commit(self) -> Iterator[str]:
        for changed_file in self.latest_commit.files:
            if changed_file.previous_filename is not None:
                yield changed_file.previous_filename
            yield changed_file.filename

    def apply_ignore_patterns(self) -> None:
        path = self.downloaded_repository_folder / self.ignore_patterns_path
        if path.exists():
            for pattern in path.lines:
                if pattern.endswith("/"):
                    pattern = f"{pattern}*"
                self.run_git("reset", pattern)

    def push_updates(self) -> None:
        self.run_git("push", "--set-upstream", "origin", self.update_branch)
        title = "Sync template changes"
        try:
            self.repository_client.create_pull(
                self.default_branch, self.update_branch, title=title, body=""
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

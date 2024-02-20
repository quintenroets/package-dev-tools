from dataclasses import dataclass

import github.Auth
from github import Github


@dataclass
class Client:
    token: str

    def __post_init__(self) -> None:
        auth = github.Auth.Token(self.token)
        self.client = Github(auth=auth)

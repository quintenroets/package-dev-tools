import cli
from package_dev_tools.actions.substitute_template_name import substitute_template_name
from package_dev_tools.models import Path


def test_substitute_template_name(repository_path: Path) -> None:
    substitute_and_verify()


def test_byte_content_skipping(repository_path: Path) -> None:
    path = Path("binary_content")
    path.byte_content = b"\xFF"
    commands = (
        ("git add", path),
        ("git commit --no-verify -m", "add byte file with byte content"),
    )
    for command in commands:
        cli.get(*command)
    substitute_and_verify()


def substitute_and_verify() -> None:
    project_name = "package-dev-tools"
    substitute_template_name(project_name=project_name)
    info = Path("pyproject.toml").text
    assert project_name in info

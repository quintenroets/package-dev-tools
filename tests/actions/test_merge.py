from package_dev_tools.actions.instantiate_new_project.git import GitInterface
from package_dev_tools.actions.template_sync.merge import Merger
from package_dev_tools.models import Path


def test_merge_template_changes(
    template_directory: Path,
    repository_directory: Path,
    repository_name: str,
) -> None:
    merger = Merger(
        repository_directory,
        template_directory,
        repository=repository_name,
    )
    merger.merge_in_template_updates()
    git = GitInterface(repository_directory)
    git.capture_output("add -A")
    status = git.capture_output("status")
    assert "pyproject.toml" in status

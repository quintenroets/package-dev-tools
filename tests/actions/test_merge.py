from package_dev_tools.actions.template_sync.merge import Merger
from package_dev_tools.models import Path
from package_dev_tools.utils import git


def test_merge_template_changes(
    template_directory: Path, repository_directory: Path
) -> None:
    merger = Merger(repository_directory, template_directory, repository="cli")
    merger.merge_in_template_updates()
    git.capture_output(repository_directory, "add -A")
    status = git.capture_output(repository_directory, "status")
    assert "pyproject.toml" in status

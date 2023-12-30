from collections.abc import Iterator

import pytest
from dev_tools.models import Path
from hypothesis import HealthCheck

suppressed_checks = (HealthCheck.function_scoped_fixture,)


@pytest.fixture
def restore_readme() -> Iterator[None]:
    saved_content = Path.readme.text
    yield
    Path.readme.text = saved_content

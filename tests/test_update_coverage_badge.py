from dev_tools.models import Path
from dev_tools.pre_commit.update_coverage_badge import update_coverage_badge
from hypothesis import HealthCheck, given, settings, strategies

suppressed_checks = (HealthCheck.function_scoped_fixture,)


@given(value=strategies.integers(min_value=0, max_value=100))
@settings(suppress_health_check=suppressed_checks)
def test_update_coverage_badge(restore_readme: None, value: int) -> None:
    update_coverage_badge(value)
    assert str(value) in Path.readme.text

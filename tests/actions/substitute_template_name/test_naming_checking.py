import string

import pytest
from hypothesis import given, strategies
from hypothesis.strategies import SearchStrategy
from package_dev_tools.actions.substitute_template_name.project import Project


def create_valid_name_strategy() -> SearchStrategy[str]:
    alphabet = *string.ascii_lowercase, *string.digits
    return strategies.text(alphabet=alphabet, min_size=1)


@given(name=create_valid_name_strategy())
def test_valid_name_acceptance(name: str) -> None:
    Project(name)


def create_invalid_name_strategy() -> SearchStrategy[str]:
    alphabet = *string.ascii_uppercase, *"_: "
    return strategies.text(alphabet=alphabet)


@given(name=create_invalid_name_strategy())
def test_invalid_name_rejection(name: str) -> None:
    with pytest.raises(ValueError, match=".*is invalid.*"):
        Project(name)

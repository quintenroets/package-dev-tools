from collections.abc import Iterator

import pytest


@pytest.fixture(autouse=True)
def suppress_output(capfd: pytest.CaptureFixture[str]) -> Iterator[None]:
    yield
    capfd.readouterr()

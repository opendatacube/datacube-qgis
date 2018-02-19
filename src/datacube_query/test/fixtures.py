import pytest

from pathlib import Path


@pytest.fixture
def data_path():
    return Path(Path(__file__).parent, 'data').absolute()


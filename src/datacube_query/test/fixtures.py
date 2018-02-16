from pathlib import Path
import pytest


@pytest.fixture
def data_path():
    return Path(Path(__file__).parent, 'data').absolute()


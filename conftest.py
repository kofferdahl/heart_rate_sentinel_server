import pytest
from server import create_patient


@pytest.fixture
def P():
    P = create_patient(1, "kro18@duke.edu", 10)
    return P

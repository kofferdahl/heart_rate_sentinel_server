from server import create_patient, is_tachycardic, update_heart_rate, \
    get_status, get_patient
import pytest
import datetime as dt


def test_create_patient():
    P = create_patient(1, "kro18@duke.edu", 10)
    assert P.user_age == 10
    assert P.attending_email == "kro18@duke.edu"
    assert P.patient_id == 1


@pytest.mark.parametrize("age, heart_rate, expected_tachycardic", [
    (0, 159, False),
    (0, 160, True),
    (1, 151, False),
    (1, 152, True),
    (2, 151, False),
    (2, 152, True),
    (3, 137, False),
    (3, 138, True),
    (4, 137, False),
    (4, 138, True),
    (5, 133, False),
    (5, 134, True),
    (7, 133, False),
    (7, 134, True),
    (8, 130, False),
    (8, 131, True),
    (11, 130, False),
    (11, 131, True),
    (12, 119, False),
    (12, 120, True),
    (15, 119, False),
    (15, 120, True),
    (16, 100, False),
    (16, 101, True),
    (35, 100, False),
    (35, 101, True),
])
def test_is_tachycardic(age, heart_rate, expected_tachycardic):
    assert is_tachycardic(age, heart_rate) == expected_tachycardic


def test_update_heart_rate(P):
    update_heart_rate(P.patient_id, 200)
    p = get_patient(P.patient_id)
    assert p.heart_rate[-1] == 200
    assert p.is_tachycardic[-1] is True


def test_get_status(P):
    update_heart_rate(P.patient_id, 200)
    output_dict = get_status(P.patient_id)

    assert output_dict["is_tachycardic"] is True

    assert output_dict["timestamp"] < dt.datetime.now()
    assert output_dict["timestamp"] > dt.datetime.now() - dt.timedelta(
        seconds=10)

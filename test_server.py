from server import create_patient


def test_create_patient():
    P = create_patient(1, "kro18@duke.edu", 10)
    assert P.user_age == 10
    assert P.attending_email == "kro18@duke.edu"
    assert P.patient_id == 1

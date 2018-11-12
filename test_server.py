from server import create_patient


def test_create_patient():
    P = create_patient(1, "kro18@duke.edu", 10)
    assert P.user_age == 10
    assert P.attending_email == "kro18@duke.edu"
    assert P.patient_id == 1
    assert not P.is_tachycardic  # Default
    assert P.heart_rate == 60  # Default
    assert not P.received_hr_info  # Indicates existence of defaults
    # b/c it hasn't received heart rate information for heart_rate and
    # is_tachycardic

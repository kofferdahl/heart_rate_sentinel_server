from pymodm import connect
from pymodm import MongoModel, fields

connect("mongodb://User:GODUKE10@ds151463.mlab.com:51463/heart-rate-sentinel")


def create_patient(patient_id, attending_email, user_age):
    p = Patient(patient_id=patient_id, attending_email=attending_email,
                user_age=user_age, is_tachycardic=False, heart_rate=60)
    p.save()
    return p


class Patient(MongoModel):
    patient_id = fields.IntegerField(primary_key=True)
    attending_email = fields.EmailField()
    user_age = fields.IntegerField()
    is_tachycardic = fields.BooleanField()
    heart_rate = fields.IntegerField()
    received_hr_info = fields.BooleanField()  # for determining if there has
    # been heart rate info that has actually been received, or if the info
    # for those fields is just the default

from pymodm import connect
from pymodm import MongoModel, fields

connect("mongodb://User:GODUKE10@ds151463.mlab.com:51463/heart-rate-sentinel")


def create_patient(patient_id, attending_email, user_age):
    p = Patient(patient_id=patient_id, attending_email=attending_email,
                user_age=user_age)
    p.save()
    return p


class Patient(MongoModel):
    patient_id = fields.IntegerField(primary_key=True)
    attending_email = fields.EmailField()
    user_age = fields.IntegerField()
    is_tachycardic = fields.ListField(field=fields.BooleanField())
    heart_rate = fields.ListField(field=fields.IntegerField())
    heart_rate_time = fields.ListField(field=fields.DateTimeField())

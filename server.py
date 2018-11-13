from pymodm import connect
from pymodm import MongoModel, fields
import datetime
from statistics import mean

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


def update_heart_rate(patient_id, heart_rate):
    p = Patient.objects.raw({"_id": patient_id}).first()

    p.heart_rate.append(heart_rate)
    p.heart_rate_time.append(datetime.datetime.now())

    age = p.user_age
    tachycardic = is_tachycardic(age, heart_rate)

    p.is_tachycardic.append(tachycardic)
    p.save()

    print(p.is_tachycardic)


def is_tachycardic(age, heart_rate):

    if age < 1:
        if heart_rate > 159:
            return True
        else:
            return False
    elif age <= 2:
        if heart_rate > 151:
            return True
        else:
            return False
    elif age <= 4:
        if heart_rate > 137:
            return True
        else:
            return False
    elif age <= 7:
        if heart_rate > 133:
            return True
        else:
            return False
    elif age <= 11:
        if heart_rate > 130:
            return True
        else:
            return False
    elif age <= 15:
        if heart_rate > 119:
            return True
        else:
            return False
    elif age > 15:
        if heart_rate > 100:
            return True
        else:
            return False


def get_status(patient_id):
    p = Patient.objects.raw({"_id": patient_id}).first()

    output_dict = {}
    output_dict["is_tachycardic"] = p.is_tachycardic[-1]
    output_dict["timestamp"] = p.heart_rate_time[-1]

    return output_dict


def get_patient(patient_id):
    p = Patient.objects.raw({"_id": patient_id}).first()
    return p


def get_heart_rate(patient_id):
    p = get_patient(patient_id)
    return p.heart_rate


def get_average_heart_rate(heart_rates):
    return mean(heart_rates)


def get_interval_average_heart_rate(heart_rates,
                                    heart_rate_times,
                                    average_heart_rate_since):

    inx_list = [inx for inx, time in enumerate(heart_rate_times) if time >=
                average_heart_rate_since]

    heart_rates_in_interval = [heart_rates[i] for i in inx_list]

    return mean(heart_rates_in_interval)

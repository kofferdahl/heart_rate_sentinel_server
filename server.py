from pymodm import connect
from pymodm import MongoModel, fields
import datetime
from statistics import mean
from flask import Flask, jsonify, request
import sendgrid
import os
from sendgrid.helpers.mail import *


connect("mongodb://User:GODUKE10@ds151463.mlab.com:51463/heart-rate-sentinel")
app = Flask(__name__)


@app.route("/api/new_patient", methods=["POST"])
def new_patient():
    req_data = request.get_json()
    patient_id = req_data["patient_id"]
    attending_email = req_data["attending_email"]
    user_age = req_data["user_age"]
    create_patient(patient_id, attending_email, user_age)
    return "200"


def create_patient(patient_id, attending_email, user_age):
    p = Patient(patient_id=patient_id, attending_email=attending_email,
                user_age=user_age)
    p.save()
    return p


class Patient(MongoModel):
    patient_id = fields.CharField(primary_key=True)
    attending_email = fields.EmailField()
    user_age = fields.IntegerField()
    is_tachycardic = fields.ListField(field=fields.BooleanField())
    heart_rate = fields.ListField(field=fields.IntegerField())
    heart_rate_time = fields.ListField(field=fields.DateTimeField())


@app.route("/api/heart_rate", methods=["POST"])
def heart_rate_post_request():
    req_data = request.get_json()
    patient_id = req_data["patient_id"]
    heart_rate = req_data["heart_rate"]

    update_heart_rate(patient_id, heart_rate)

    return "200"


def update_heart_rate(patient_id, heart_rate):
    p = Patient.objects.raw({"_id": patient_id}).first()

    p.heart_rate.append(heart_rate)
    hr_timestamp = datetime.datetime.now()

    p.heart_rate_time.append(hr_timestamp)

    age = p.user_age
    tachycardic = is_tachycardic(age, heart_rate)
    if(tachycardic):
        attending_email = str(p.attending_email)
        try:
            send_tachycardic_email(patient_id, heart_rate, hr_timestamp,
                                   attending_email)
        except Exception:
            print("Please Configure Sendgrid API Key")

    p.is_tachycardic.append(tachycardic)
    p.save()


def send_tachycardic_email(patient_id, heart_rate, hr_timestamp,
                           attending_email):

    date = hr_timestamp.strftime("%B %d, %Y")
    time = hr_timestamp.strftime("%H:%M")
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("tachycardia_alert_server@bme590.com")
    to_email = Email(attending_email)
    subject = "Tachycardia alert for Patient ID " + patient_id
    content = Content("text/plain",
                      "ALERT: Patient with ID " + patient_id + " was "
                      "tachycardic on " + date + " at " + time + " with heart "
                      "rate of " + str(heart_rate) + " BPM.")

    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())


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


@app.route("/api/status/<patient_id>", methods=["GET"])
def status(patient_id):
    output_status = get_status(patient_id)
    return jsonify(output_status)


def get_status(patient_id):
    p = Patient.objects.raw({"_id": patient_id}).first()

    output_dict = {}
    output_dict["is_tachycardic"] = p.is_tachycardic[-1]
    output_dict["timestamp"] = p.heart_rate_time[-1]

    return output_dict


def get_patient(patient_id):
    p = Patient.objects.raw({"_id": patient_id}).first()
    return p


@app.route("/api/heart_rate/<patient_id>", methods=["GET"])
def get_heart_rate_data(patient_id):
    hr = get_heart_rate(patient_id)
    return jsonify(hr), 200


def get_heart_rate(patient_id):
    p = get_patient(patient_id)
    return p.heart_rate


@app.route("/api/heart_rate/average/<patient_id>", methods=["GET"])
def average_heart_rate(patient_id):
    hr = get_heart_rate(patient_id)
    mean_hr = get_average_heart_rate(hr)
    return jsonify(mean_hr), 200


def get_average_heart_rate(heart_rates):
    return mean(heart_rates)


@app.route("/api/heart_rate/interval_average", methods=["GET"])
def interval_average():
    req_data = request.get_json()
    patient_id = req_data["patient_id"]
    heart_rate_average_since = req_data["heart_rate_average_since"]
    interval_timestamp = datetime.datetime.strptime(
        heart_rate_average_since, '%Y-%m-%d %H:%M:%S.%f')

    heart_rates = get_heart_rate(patient_id)
    p = get_patient(patient_id)
    heart_rate_times = p.heart_rate_time

    int_avg_hr = get_interval_average_heart_rate(heart_rates,
                                                 heart_rate_times,
                                                 interval_timestamp)

    return jsonify(int_avg_hr), 200


def get_interval_average_heart_rate(heart_rates,
                                    heart_rate_times,
                                    average_heart_rate_since):

    inx_list = [inx for inx, time in enumerate(heart_rate_times) if time >=
                average_heart_rate_since]

    heart_rates_in_interval = [heart_rates[i] for i in inx_list]

    return mean(heart_rates_in_interval)


if __name__ == "__main__":
    app.run(host="127.0.0.1")

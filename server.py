from pymodm import connect
from pymodm import MongoModel, fields
import datetime
from statistics import mean
from flask import Flask, jsonify, request
import sendgrid
import os
from sendgrid.helpers.mail import *
import numbers
import logging

connect("mongodb://User:GODUKE10@ds151463.mlab.com:51463/heart-rate-sentinel")
app = Flask(__name__)
logging.basicConfig(filename="HR_Sentinel_Server_Logs.txt",
                    format='%(asctime)s %(levelname)s:%(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')


@app.route("/api/new_patient", methods=["POST"])
def new_patient():
    """Handles webservice function call for creating a new patient

    This method expects there to be a json style dictionary input from the
    post request, with fields for patient_id (unique string identifying the
    patient), attending_email, and user_age (patient age).

    Example:
        patient_data = {"patient_id": "1", "attending_email": kro18@duke.edu,
        "user_age": 10}

        r = requests.post(ip + "/api/new_patient", json=patient_data)

    Returns:
        status_code (str): Status code indicating successful execution
    """
    req_data = request.get_json()
    try:
        patient_id = req_data["patient_id"]
        attending_email = req_data["attending_email"]
        user_age = req_data["user_age"]
        create_patient(patient_id, attending_email, user_age)
        status_code = "200"
        return status_code

    except NameError:
        print("Error: Input dictionary does not specify the correct "
              "parameters.")
        logging.error("Input dictionary does not specify the correct "
                      "parameters.")
        status_code = "400"
        return status_code


def create_patient(patient_id, attending_email, user_age):
    """Creates a patient in the mongo database

    Args:
        patient_id (str): Unique ID for the patient
        attending_email (str): Email address of attending physician
        user_age (float): Age of the patient

    Returns:
        p (Patient): Patient object with specified parameters
    """
    p = Patient(patient_id=patient_id, attending_email=attending_email,
                user_age=user_age)
    p.save()
    return p


class Patient(MongoModel):
    """Patient object for the Mongo database

    Attributes:
        patient_id (str): Unique ID for the patient
        attending_email (str): Email address of attending for patient
        user_age (float): Patient age
        is_tachycardiac (list): List of booleans for whether patient is
                                tachycardic at time of receiving heart rate
                                measurement
        heart_rate (list): List of floats containing heart rates
        heart_rate_time (list): List of DateTime objects with heart rate
                                time stamps

    """
    patient_id = fields.CharField(primary_key=True)
    attending_email = fields.EmailField()
    user_age = fields.FloatField()
    is_tachycardic = fields.ListField(field=fields.BooleanField())
    heart_rate = fields.ListField(field=fields.FloatField())
    heart_rate_time = fields.ListField(field=fields.DateTimeField())


@app.route("/api/heart_rate", methods=["POST"])
def heart_rate_post_request():
    """handles updating the heart rate from the web service post request

    This function is expecting to have a json style dictionary input in the
    post request, with fields for patient_id and heart_rate.

    Example:
        hr_data = {"patient_id": "1", "heart_rate": 100}
        r = requests.post(ip + "/api/heart_rate", json=hr_data)

    Returns:
        status_code (str): Status code indicating successful execution
    """
    req_data = request.get_json()
    try:
        patient_id = req_data["patient_id"]
        heart_rate = req_data["heart_rate"]
    except NameError:
        print("Error: Invalid input dictionary parameters")
        logging.error("invalid input dictionary parameters")
        status_code = "400"
        return status_code

    try:

        update_heart_rate(patient_id, heart_rate)
    except ValueError:
        print("error: invalid patient ID or heart rate")
        logging.error("invalid patient ID or heart rate")
        status_code = "400"
        return status_code
    status_code = "200"
    return status_code


def update_heart_rate(patient_id, heart_rate):
    """Updates patient heart rate in webservice and iniatites sending of
    tachycardia email if tachycardic

    Args:
        patient_id (str): Unique patient identification string
        heart_rate (float): Patient heart rate in BPM

    Returns: None
    """
    try:
        p = Patient.objects.raw({"_id": patient_id}).first()
        if not isinstance(heart_rate, numbers.Number):
            raise ValueError

        p.heart_rate.append(heart_rate)
        hr_timestamp = datetime.datetime.now()

        p.heart_rate_time.append(hr_timestamp)

        age = p.user_age
        try:
            tachycardic = is_tachycardic(age, heart_rate)
            if (tachycardic):
                attending_email = str(p.attending_email)
                try:
                    send_tachycardic_email(patient_id, heart_rate,
                                           hr_timestamp,
                                           attending_email)

                except Exception:
                    print("Please Configure Sendgrid API Key")
                    logging.error("Sendgrid API key is not configured")

            p.is_tachycardic.append(tachycardic)
            p.save()
        except TypeError:
            print("Error: Non-numerical inputs for age or heart_rate")
            logging.error("Invalid age or heart_rate input data types")

    except:
        raise ValueError


def send_tachycardic_email(patient_id, heart_rate, hr_timestamp,
                           attending_email):
    """Sends email to attending physician when patient is tachycardic

    Args:
        patient_id (str): Unique patient identification string
        heart_rate (float): Patient heart rate (BPM)
        hr_timestamp (DateTime): time of heart rate measurement
        attending_email (str): Email address of attending physician

    Returns: None
    """
    try:
        date = hr_timestamp.strftime("%B %d, %Y")
        time = hr_timestamp.strftime("%H:%M")
        sg = sendgrid.SendGridAPIClient(
            apikey=os.environ.get('SENDGRID_API_KEY'))
        from_email = Email("tachycardia_alert_server@bme590.com")
        to_email = Email(attending_email)
        subject = "Tachycardia alert for Patient ID " + patient_id
        content = Content("text/plain",
                          "ALERT: Patient with ID " + patient_id + " was "
                          "tachycardic on " + date + " at " + time + " with "
                          "heart rate of " + str(heart_rate) + " BPM.")

        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
    except ValueError:
        print("error: datetime string improperly formatted")
        logging.error("Improperly formatted datetime string.")


def is_tachycardic(age, heart_rate):
    """Determines whether or not a patient is tachycardic

    Args:
        age (float): Patient age
        heart_rate (float): Patient heart rate (BPM)

    Returns:
        Boolean that is true when patient is tachycardic
    """
    if not isinstance(heart_rate, numbers.Number):
        raise TypeError
    if not isinstance(age, numbers.Number):
        raise TypeError

    if age <= 2/365:
        if heart_rate > 159:
            return True
        else:
            return False
    elif age <= 6/365:
        if heart_rate > 166:
            return True
        else:
            return False
    elif age <= 3/52:
        if heart_rate > 182:
            return True
        else:
            return False
    elif age <= 2/12:
        if heart_rate > 179:
            return True
        else:
            return False
    elif age <= 5/12:
        if heart_rate > 186:
            return True
        else:
            return False
    elif age <= 364/365:
        if heart_rate > 169:
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
    """Wrapper function for handling webservice api call for status

    The webservice command is expecting a patient ID string.

    Example:
        r = requests.post(ip + "/api/status/1")

    Args:
        patient_id (str): Unique patient identification string

    Returns:
        output_status (dict): A dictionary with entries "is_tachycardic" for if
                              the patient is tachycardic, and an entry
                              "timestamp" indicating the time at which this
                              assessment was made.
    """
    output_status = get_status(patient_id)
    return jsonify(output_status), 400


def get_status(patient_id):
    """Gets the tachycardic status of patient and associated time stamp

    Args:
        patient_id (str): Unique patient identification string

    Returns:
        output_status (dict): A dictionary with entries "is_tachycardic" for if
                              the patient is tachycardic, and an entry
                              "timestamp" indicating the time at which this
                              assessment was made.
    """
    try:
        p = Patient.objects.raw({"_id": patient_id}).first()
        output_dict = {}
        output_dict["is_tachycardic"] = p.is_tachycardic[-1]
        output_dict["timestamp"] = p.heart_rate_time[-1]
        return output_dict
    except:
        print("Invalid patient ID")
        logging.error("Invalid patient ID.")


def get_patient(patient_id):
    """Gets a patient object based on patient ID.

    Args:
        patient_id: Unique patient identification string

    Returns:
        p (Patient): Patient object from Mongo DB database associated with
                     patient ID string
    """
    p = Patient.objects.raw({"_id": patient_id}).first()
    return p


@app.route("/api/heart_rate/<patient_id>", methods=["GET"])
def get_heart_rate_data(patient_id):
    """Handler function for webservice call to get patient heart rate

    The webservice is expecting a string with the patient_id.

    Example:
        r = requests.post(ip + "/api/heart_rate/1")
        hr = r.json # Returns a list of heart rates
    Args:
        patient_id (str): Unique patient identification string

    Returns:
        hr (float): A jsonified list of floats containing all patient heart
                    rates
    """

    hr = get_heart_rate(patient_id)
    return jsonify(hr), 200


def get_heart_rate(patient_id):
    """Gets the full list of recorded patient heart rates

    Args:
        patient_id (str): Unique patient identification string

    Returns:
        heart_rates (list): A list of all recorded patient heart rates (in BPM)
    """
    p = get_patient(patient_id)
    heart_rates = p.heart_rate
    return heart_rates


@app.route("/api/heart_rate/average/<patient_id>", methods=["GET"])
def average_heart_rate(patient_id):
    """Handler method for managing webservice call for average heart rate

    This function is expecting the get request to specify a valid patient_id

    Example:
        r = request.get(ip + "/api/heart_rate/average/1"
        avg_hr = r.json() # Average heart rate for patient 1

    Args:
        patient_id (str): Unique patient identification string

    Returns:
        mean_hr (float): A jsonified mean heart rate across all heart rate
                         measurements
    """

    hr = get_heart_rate(patient_id)
    mean_hr = get_average_heart_rate(hr)
    return jsonify(mean_hr), 200


def get_average_heart_rate(heart_rates):
    """Gets the average heart rate from a list of heart rates

    Args:
        heart_rates (list): A list of floats with all recorded heart rates

    Returns:
        mean_hr (float): The mean of all heart rates in that list

    """
    mean_hr = mean(heart_rates)
    return mean_hr


@app.route("/api/heart_rate/interval_average", methods=["GET"])
def interval_average():
    """Handler function for webservice calling functions to get mean heart
    rate over a specified interval.

    interval_average takes in parameters from the webservice call, which are
    retrieved using request.get_json, which should get a dictionary
    containing the patient ID and a string specifying time period for the
    interval. Note that the heart_rate_average_since string must be in the
    format '%Y-%m-%d %H:%M:S.%f'

    Example:
        data = {"patient_id": 1, "heart_rate_avg_since": timestamp_string}
        r = requests.get(ip + "/api/heart_rate/interval_average", json=data)
        int_avg = r.json() # Average heart rate since timestamp string

    Returns:
        int_avg_hr (float): Average heart rate over a specified interval.
    """
    req_data = request.get_json()
    try:
        patient_id = req_data["patient_id"]
        heart_rate_average_since = req_data["heart_rate_average_since"]

        try:
            interval_timestamp = datetime.datetime.strptime(
                heart_rate_average_since, '%Y-%m-%d %H:%M:%S.%f')
            heart_rates = get_heart_rate(patient_id)
            p = get_patient(patient_id)
            heart_rate_times = p.heart_rate_time

            int_avg_hr = get_interval_average_heart_rate(heart_rates,
                                                         heart_rate_times,
                                                         interval_timestamp)

            return jsonify(int_avg_hr), 200
        except ValueError:
            print("Error: Improperly formatted datetime string.")
            logging.error("Improperly formatted datetime string.")
            return "400"

    except NameError:
        print("Error: Invalid input dictionary entries.")
        logging.error("Invalid input dictionary entries.")
        return "400"


def get_interval_average_heart_rate(heart_rates,
                                    heart_rate_times,
                                    average_heart_rate_since):
    """Gets the average heart rate in a specified interval

    Args:
        heart_rates (list): List of all patient heart rates
        heart_rate_times (list): List of timestamps of heart rate recording
                                 times
        average_heart_rate_since: Datetime object indicating the last heart
                                  rate time in the interval calculation.

    Returns:
        int_mean (float): Interval mean heart rate
    """

    inx_list = [inx for inx, time in enumerate(heart_rate_times) if time >=
                average_heart_rate_since]

    heart_rates_in_interval = [heart_rates[i] for i in inx_list]

    int_mean = mean(heart_rates_in_interval)
    return int_mean


if __name__ == "__main__":
    app.run(host="127.0.0.1")

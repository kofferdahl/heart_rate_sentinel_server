import requests
import datetime as dt
import time

ip = "http://vcm-7247.vm.duke.edu:5000"
# ip = "127.0.0.1:5000" # for local hosting

# INSERT YOUR EMAIL ADDRESS HERE!
email = "kro18@duke.edu"

# Create new patient
patient_data = {"patient_id": "1", "attending_email": email, "user_age": 10}
r = requests.post(ip + "/api/new_patient", json=patient_data)

# Add first heart rate, not tachycardic for this age
hr_data = {"patient_id": "1", "heart_rate": 100}
r = requests.post(ip + "/api/heart_rate", json=hr_data)

# Get patient status dictionary
r = requests.get(ip + "/api/status/1")
print("Status: " + str(r.json()))

# Get time stamp for interval_avg calculation (which will exclude first
# heart rate value.
time_stamp = dt.datetime.now()
ts_str = str(time_stamp)

# needs to pause briefly so that there is a detectable amount of time
# between this timestamp and the next recorded heart rate data point
time.sleep(0.25)

# Add another patient heart rate data point
# Since this is tachycardic, you should receive a tachycardia alert email at
#  the email address specified at the beginning of this script.
hr_data = {"patient_id": "1", "heart_rate": 200}
r = requests.post(ip + "/api/heart_rate", json=hr_data)

# Get status (is_tachycardic should be true)
r = requests.get(ip + "/api/status/1")
print("Status: " + str(r.json()))

# Add another patient heart rate data point
hr_data = {"patient_id": "1", "heart_rate": 100}
r = requests.post(ip + "/api/heart_rate", json=hr_data)

# Get a list of all recorded patient heart rates
r = requests.get(ip + "/api/heart_rate/1")
print("heart rates: " + str(r.json()))

# Get the mean of all recorded heart rates
r = requests.get(ip + "/api/heart_rate/average/1")
print("average heart rate: " + str(r.json()) + " BPM")

# Get the interval average for all heart rates recorded after the timestamp
# generated above (should be all except the first data point)
int_avg_data = {"patient_id": "1", "heart_rate_average_since": ts_str}
r = requests.get(ip + "/api/heart_rate/interval_average", json=int_avg_data)
int_avg = r.json()
print("interval average: " + str(int_avg) + " BPM")

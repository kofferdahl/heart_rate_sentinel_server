# BME 590: Heart Rate Sentinel Server

## General Usage
The webserver address is http://vcm-7247.vm.duke.edu/5000
<s>You can confirm that the webservice is working by going to http://vcm-7247.vm.duke.edu/5000/ where you should see plain text that says "I'm working."</s> [The virtual machine is no longer running on Duke's servers.]
If the webserver is not working, the version of server.py in this repository is currently configured to run on a local machine. Simply pip install requirements.txt, and then enter `python server.py` at the command line to host the webserver locally. 

## Demo Script
demo.py should contain a comprehensive demo showing the functionality of all of the web API.
Be sure to change the email address at the top of the file so that you receive the tachycardic alert email.

You should be able to just run this as `python demo.py` in a virtual environment where requirements.txt has been installed.
If the vcm server is not working, uncomment `ip = 127.0.0.1:5000/` at the top of the file to run on your local machine, after running `python server.py` in a separate command prompt window.

## General Information
server.py is the main file containing both the webservice commands and the underlying python functionality for handling those requests.
test_server.py contains all of the tests for python functions in server.py
dmeo.py contains a standalone, fully functioning demo of all components of the webservice 
conftest.py configures certain global variables for test_server.py

## Nice Features
There's a few things that I'm somewhat proud of that went beyond the requirements of the assignment, and I would like to highlight these for grading considerations.

* Existence of a standalone demo.py script
* Use of a database to handle patients
* Ability to handle tachycardia cutoffs for all ages, including fractional ages for those less than 1 year old.

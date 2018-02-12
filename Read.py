#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import time
import os
import RPi.GPIO as GPIO
import MFRC522
import signal
import subprocess
import requests
from requests.auth import HTTPBasicAuth

sadra_server = 'https://xsadra.cf/checkin/data.php'
server = os.environ['RC_CHECK_IN_SERVER']
username = os.environ['RC_CHECK_IN_USERNAME']
password = os.environ['RC_CHECK_IN_PASSWORD']

continue_reading = True

# Set gpio mode for leds
subprocess.call(["gpio", "mode", "0", "out"])
subprocess.call(["gpio", "mode", "1", "out"])

def log(msg):
    print time.strftime("%Y-%m-%d %H:%M") + ": " + msg
    sys.stdout.flush()

def green(on):
    subprocess.call(["gpio", "write", "0", "1" if on else "0"])

def red(on):
    subprocess.call(["gpio", "write", "1", "1" if on else "0"])

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    log("Ctrl+C captured, ending read.")
    continue_reading = False
    GPIO.cleanup()

def blink_error():
    for i in range(0,3):
        red(True)
        time.sleep(0.1)
        red(False)
        time.sleep(0.1)

def blink_hello():
    red(True)
    green(True)
    time.sleep(1)
    red(False)
    green(False)

def blink_check_in():
    green(True)
    time.sleep(1)
    green(False)

def blink_check_out():
    red(True)
    time.sleep(1)
    red(False)

# Welcome message
log("Welcome to the rc-check-in-card-reader! Press Ctrl-C to stop.")

# Contact the backend on start up
resp = requests.get(server + '/hello', auth=HTTPBasicAuth(username,password))
helloStatus = resp.status_code
log("Request /hello status: " + str(helloStatus))
if helloStatus == 200:
    blink_hello()
else:
    blink_error()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:

    # Scan for cards
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    #print "status"+str(status)+","+str(TagType)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        log("Card detected")

    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:

        uidString = str(uid[0]) + "," + str(uid[1]) + "," + str(uid[2]) + "," + str(uid[3])

        # Print UID
        log("Card UID: " + uidString)

        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)

        # Check if authenticated
        if status == MIFAREReader.MI_OK:

            MIFAREReader.MFRC522_Read(8)
            MIFAREReader.MFRC522_StopCrypto1()

            resp = requests.get(server + '/people/' + uidString + '/checkin', auth=HTTPBasicAuth(username, password))

            checkinStatus = resp.status_code
            log("Request /checkin response: " + str(checkinStatus))

            if checkinStatus == 200:
                dict = resp.json()
                name = dict['name']
                checkedIn = dict['checkedIn']
                log(name + ": " + str(checkedIn))
                if checkedIn == True:
                    blink_check_in()
                else:
                    blink_check_out()

		#Send data to Sadra Server for Check in BOT
                requests.post(sadra_server, data={'userid': uidString, 'checkedIn': checkedIn})

            else:
                blink_error()

            time.sleep(2)

        else:
            log("Authentication error")
            blink_error()

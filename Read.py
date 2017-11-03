#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal
import time
import subprocess
import requests
from requests.auth import HTTPBasicAuth
#import os
import time

server = 'https://rc-check-in-backend.herokuapp.com'
#username = os.environ['RC_CHECK_IN_USERNAME']
#password = os.environ['RC_CHECK_IN_PASSWORD']

continue_reading = True

# Set gpio mode for leds
subprocess.call(["gpio", "mode", "0", "out"])
subprocess.call(["gpio", "mode", "1", "out"])

def log(msg):
    print time.strftime("%Y-%m-%d %H:%M") + ": " + msg

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    log("Ctrl+C captured, ending read.")
    continue_reading = False
    GPIO.cleanup()

def blink_error():
    subprocess.call(["gpio", "write", "1", "1"])
    time.sleep(0.1)
    subprocess.call(["gpio", "write", "1", "0"])
    time.sleep(0.1)
    subprocess.call(["gpio", "write", "1", "1"])
    time.sleep(0.1)
    subprocess.call(["gpio", "write", "1", "0"])
    time.sleep(0.1)
    subprocess.call(["gpio", "write", "1", "1"])
    time.sleep(0.1)
    subprocess.call(["gpio", "write", "1", "0"])
    time.sleep(0.1)

def blink_hello():
    subprocess.call(["gpio", "write", "0", "1"])
    subprocess.call(["gpio", "write", "1", "1"])
    time.sleep(1)
    subprocess.call(["gpio", "write", "0", "0"])
    subprocess.call(["gpio", "write", "1", "0"])

def blink_check_in():
    subprocess.call(["gpio", "write", "0", "1"])
    time.sleep(1)
    subprocess.call(["gpio", "write", "0", "0"])

def blink_check_out():
    subprocess.call(["gpio", "write", "1", "1"])
    time.sleep(1)
    subprocess.call(["gpio", "write", "1", "0"])

# Welcome message
log("Welcome to the rc-check-in-card-reader! Press Ctrl-C to stop.")

# Contact the backend on start up
#resp = requests.get(server + '/hello', auth=HTTPBasicAuth(username,password))
resp = requests.get(server + '/hello')
helloStatus = resp.status_code
log("Request /hello status:" + str(helloStatus)) 
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

    #print "status"+str(status)+","+str(uid) 

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:

        uidString = str(uid[0]) + "," + str(uid[1]) + "," + str(uid[2]) + "," + str(uid[3])

        # Print UID
        log("Card UID: " + uidString)
    
        # This is the default key for authentication
        # blue chip:
        #key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        # white card:
        #key = [0xD3,0xF7,0xD3,0xF7,0xD3,0XF7]
        
        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)

        # Authenticate
        #status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

        #print "status:" + str(status)

        # Check if authenticated
        if status == MIFAREReader.MI_OK:
            MIFAREReader.MFRC522_Read(8)
            MIFAREReader.MFRC522_StopCrypto1()
            #print "Authentication success"
#            resp = requests.get(server + '/people/' + uidString + '/checkin', auth=HTTPBasicAuth(username,password))
            resp = requests.get(server + '/people/' + uidString + '/checkin')
            checkinStatus = resp.status_code
            log("Request /checkin response: " + str(checkinStatus))
            if checkinStatus == 200:
                if resp.content == 'true':
                    blink_check_in()
		else:
                    blink_check_out()
            else:
                blink_error()
            time.sleep(5)
        else:
            log("Authentication error")
            blink_error()

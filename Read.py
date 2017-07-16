#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal
import time
import subprocess
import requests

server = 'http://192.168.1.115:8080'

continue_reading = True

subprocess.call(["gpio", "mode", "0", "out"])
subprocess.call(["gpio", "mode", "1", "out"])

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()

def error():
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

def checkin():
    subprocess.call(["gpio", "write", "0", "1"])
    time.sleep(0.5)
    subprocess.call(["gpio", "write", "0", "0"])

def checkout():
    subprocess.call(["gpio", "write", "1", "1"])
    time.sleep(0.5)
    subprocess.call(["gpio", "write", "1", "0"])


# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
print "Welcome to the MFRC522 data read example"
print "Press Ctrl-C to stop."

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:
    
    # Scan for cards    
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    #print "status"+str(status) 

    # If a card is found
    if status == MIFAREReader.MI_OK:
        print "Card detected"

    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    #print "status"+str(status) 

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:

        uidString = str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])

        # Print UID
        print "Card read UID: "+uidString
    
        # This is the default key for authentication
        # blue chip:
        #key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        # white card:
        key = [0xD3,0xF7,0xD3,0xF7,0xD3,0XF7]
        
        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)

        # Authenticate
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

        # Check if authenticated
        if status == MIFAREReader.MI_OK:
            MIFAREReader.MFRC522_Read(8)
            MIFAREReader.MFRC522_StopCrypto1()
            print "Authentication success"
            resp = requests.get(server+'/people/'+uidString+'/checkin')
            checkinStatus = resp.status_code
            print "checkin response: " + str(checkinStatus)
            if checkinStatus == 200:
                if resp.content == 'true':
                    checkin()
		else:
                    checkout()
            else:
                print "checkin error"
                error()
            time.sleep(10)
        else:
            print "Authentication error"
            error()

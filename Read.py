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
import Adafruit_CharLCD as LCD

#sadra_server = 'https://xsadra.cf/checkin/data.php'
server = os.environ['RC_CHECK_IN_SERVER']
username = os.environ['RC_CHECK_IN_USERNAME']
password = os.environ['RC_CHECK_IN_PASSWORD']

continue_reading = True


# Set gpio mode for leds
#subprocess.call(["gpio", "mode", "0", "out"])
#subprocess.call(["gpio", "mode", "1", "out"])

def LCDInit()
    # Please note that are using BMC number like (GPIO-18) and not raspberry pi pins number
    lcd_rs        = 18
    lcd_en        = 23
    lcd_d4        = 12
    lcd_d5        = 16
    lcd_d6        = 20
    lcd_d7        = 21
    lcd_backlight = 4
    lcd_columns = 16
    lcd_lines  = 2
    return LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5,
                            lcd_d6, lcd_d7, lcd_columns, lcd_lines,
                            lcd_backlight)
def lcd_log(message)
    #lcd.message('IP %s' %(ipaddr))
    if len(message > 16)
        lcd.message('%s\n' %(message[0:16]) )
        lcd.message(message[16:])
    else
        lcd.message(message)
    time.sleep(5)
    lcd.clear()
    
    

def log(msg):
    print time.strftime("%Y-%m-%d %H:%M") + ": " + msg
    sys.stdout.flush()

#def green(on):
#    subprocess.call(["gpio", "write", "0", "1" if on else "0"])

#def red(on):
#    subprocess.call(["gpio", "write", "1", "1" if on else "0"])

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
    lcd_log('Checked\nIn')
    #green(True)
    #time.sleep(1)
    #green(False)

def blink_check_out():
    lcd_log('Checked\nOut')
    #red(True)
    #time.sleep(1)
    #red(False)

lcd = LCDInit()
# Welcome message for LCD and console
lcd.message('Welcome ...')
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

            #Send data to Sadra Server for Check in BOT
#            requests.post(sadra_server,data={'userid': uidString})

            resp = requests.get(server + '/people/' + uidString + '/checkin', auth=HTTPBasicAuth(username,password))

            checkinStatus = resp.status_code
            log("Request /checkin response: " + str(checkinStatus))
            if checkinStatus == 200:
                if resp.content == 'true':
                    blink_check_in()
		else:
                    blink_check_out()
            else:
                blink_error()
            #time.sleep(5)
        else:
            log("Authentication error")
            blink_error()

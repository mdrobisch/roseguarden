__author__ = 'drobisch'
#!/usr/bin/env python
# -*- coding: utf8 -*-

import signal

import RPi.GPIO as GPIO

import MFRC522

continue_reading = True
auth_failed = False

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:
    #MIFAREReader = MFRC522.MFRC522()

    # Scan for cards
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        print "Card detected"

    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:

        # Print UID
        print "Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])

        # This is the default key for authentication
        key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]

        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)


        newkey = []
        newkeystring = '00-00-00-00-00-00'
        for x in newkeystring.split('-'):
            newkey.append(int(x, 16))

        secret = []
        secretstring = '35-B9-68-19-F1-B5-C7-03-35-B9-68-19-F1-B5-C7-03'
        for x in secretstring.split('-'):
            secret.append(int(x, 16))

        print "Old key is: " + str(key)
        print "New key is: " + str(newkey)
        print "Secret is: " + str(secret)

        cardAuthSector = 4
        cardAuthBlock = 1

        SecretBlockAddr = cardAuthSector * 4 + cardAuthBlock
        TrailerBlockAddr = cardAuthSector * 4 + 3

        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, SecretBlockAddr, newkey, uid)
        # Check if authenticated
        if status == MIFAREReader.MI_OK:

            # Variable for the data to write
            data = []

            # Fill the data with 0xFF
            for x in range(0,16):
                data.append(0xFF)

            print "Read Secret:"
            # Read block 8
            result = MIFAREReader.MFRC522_Read(SecretBlockAddr)
            print result
            print "\n"

            print "Write new Secret:"
            # Write the data
            MIFAREReader.MFRC522_Write(SecretBlockAddr, secret)
            print "\n"

            print "Read back secret:"
            # Check to see if it was written
            result = MIFAREReader.MFRC522_Read(SecretBlockAddr)
            print result
            print "\n"

            data = []
            # Fill the data with 0x00
            for x in range(0,16):
                data.append(0x00)

            print "Clear secret:"
            MIFAREReader.MFRC522_Write(SecretBlockAddr, data)
            print "\n"

            print "Read back cleared secret:"
            # Check to see if it was written
            result = MIFAREReader.MFRC522_Read(SecretBlockAddr)
            print result
            print "\n"

        else:
            print "Authentication error"

        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, TrailerBlockAddr, newkey, uid)

        # Check if authenticated
        if status == MIFAREReader.MI_OK :
            print "Read TrailerBlock :"
            # Read block 8
            result = MIFAREReader.MFRC522_Read(TrailerBlockAddr)
            print result

            for x in range(0,6):
                result[x] = 0xFF
            print result

            print "Write new treiler:"
            # Write the data
            MIFAREReader.MFRC522_Write(TrailerBlockAddr, result)
            print "\n"

            print "Read back trailer:"
            # Check to see if it was written
            result = MIFAREReader.MFRC522_Read(TrailerBlockAddr)
            print result
            print "\n"

            print "\n"

            # Stop
            MIFAREReader.MFRC522_StopCrypto1()

            # Make sure to stop reading for cards
            continue_reading = False
        else:
            print "Authentication error"

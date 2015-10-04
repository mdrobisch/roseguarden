__author__ = 'drobisch'

import platform


class GPIOStateMockup:
    # pin configuration
    OUT = 0
    IN = 1

    # pin states
    LOW = 0
    HIGH = 1

    def __init__(self):
        self.inputstate = self.LOW
        self.outputstate = self.LOW

    def getinput(self):
        return self.inputstate

    def getoutput(self):
        return self.outputstate

    def setinput(self, state):
        self.inputstate = state

    def setoutput(self, state):
        self.outputstate = state


class GPIOWrapper:
    # suppported modes
    UNKNOWN = 0
    BOARD = 1
    BCM = 2

    # pin configuration
    OUT = 0
    IN = 1

    # pin states
    LOW = 0
    HIGH = 1

    def __init__(self, statemockup):
        self.statemockup = statemockup
        self.mode = self.UNKNOWN

    def setmode(self, mode):
        self.mode = mode
        if mode == self.BOARD:
            print "GPIO: Using BOARD pin numbering"
        else:
            if mode == self.BCM:
                print "GPIO: Using BCM pin numbering"
            else:
                print "GPIO: Uknown mode"
        return None

    def input(self, channel):
        print "GPIO: Get " + channel + " input"
        return self.statemockup.getinput

    def output(self, channel, state):
        if (state == self.HIGH):
            print "GPIO: Set " + channel + " (HIGH)"
        else:
            print "GPIO: Reset " + channel + " (LOW)"

    def cleanup(self, channel):
        print "GPIO: Cleanup channel " + channel

    def setup(self, channel, type):
        print "GPIO: Setup GPIO " + str(channel) + " to " + str(type)


if platform.platform_getType() == platform.RASPBERRY_PI:
    try:
        import RPi.GPIO as GPIO

        print "GPIO: Using RPi.GPIO as GPIO"
        GPIOMockup = None
        GPIO.setmode(GPIO.BOARD)
    except RuntimeError:
        print(
            "Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")
else:
    print "GPIO: Using GPIOWrapper as GPIO"
    GPIOMockup = GPIOStateMockup()
    GPIO = GPIOWrapper(GPIOMockup)
    GPIO.setmode(GPIO.BOARD)





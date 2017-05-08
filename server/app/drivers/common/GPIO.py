__author__ = 'drobisch'

import app.platform
import app.logging

class GPIOStubState:
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


class GPIOStub:
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
            app.logging.log("GPIO_LOG", "GPIO: Using BOARD pin numbering")
        else:
            if mode == self.BCM:
                app.logging.log("GPIO_LOG", "GPIO: Using BCM pin numbering")
            else:
                app.logging.log("GPIO_LOG", "GPIO: Uknown mode")
        return None

    def input(self, channel):
        app.logging.log("GPIO_LOG", "GPIO: Get " + channel + " input")
        return self.statemockup.getinput

    def output(self, channel, state):
        if (state == self.HIGH):
            app.logging.log("GPIO_LOG", "GPIO: Set " + str(channel) + " (HIGH)")
        else:
            app.logging.log("GPIO_LOG", "GPIO: Reset " + str(channel) + " (LOW)")

    def cleanup(self, channel):
        app.logging.log("GPIO_LOG", "GPIO: Cleanup channel " + channel)

    def setup(self, channel, type, initial):
        app.logging.log("GPIO_LOG", "GPIO: Setup GPIO " + str(channel) + " to " + str(type))


if app.platform.platform_getType() == app.platform.RASPBERRY_PI or app.platform.platform_getType() == app.platform.RASPBERRY_PI_2:
    try:
        import RPi.GPIO as GPIO

        print "INFO: Using RPi.GPIO as GPIO"
        GPIOMockup = None
        GPIO.setmode(GPIO.BOARD)
    except RuntimeError:
        print(
            "Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")
else:
    print "WARNING: Using GPIOWrapper as GPIO"
    GPIOState = GPIOStubState()
    GPIO = GPIOStub(GPIOStubState)
    GPIO.setmode(GPIO.BOARD)





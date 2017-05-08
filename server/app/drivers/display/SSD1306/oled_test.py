import threading
import os
from smbus2 import SMBus
import oled_device, oled_render
from PIL import ImageFont
import json


displayLock = threading.RLock()

class Worker():
    def __init__(self):
        self.pmuBusIntialized = False
        self.oledDeviceIntialized = False
        self.padding = 2
        self.oldText = ""
        self.oldX = 0
        self.oldY = 0
        self.Text = "Test"
        print "initialized worker ..."

    def run(self):
        print "started worker ..."
        self.font = ImageFont.load_default()

        try:
            print "intialize i2c ..."
            self.pmuBus = SMBus(1,False)
            self.pmuBusIntialized = True
        except:
            print "error while setup GPIOs, cleaning up ..."
            self.pmuBusIntialized = False

        try:
            print "intialize oled2-display ..."
            self.oledDevice = oled_device.ssd1306(port=1, address=0x3c)
            self.oledCanvas = oled_render.canvas(self.oledDevice)
            self.oledDevice.clear()
            self.oledDeviceIntialized = True
        except:
            print "error while setup oled2 display, cleaning up ..."
            self.oledDeviceIntialized = False
            raise


        print "display thread ..."
        self.displayThr = threading.Timer(0.5, self.display_cycle)
        self.displayThr.start()

    def draw_test(self, canvas):
        # Draw some shapes.
        # First define some constants to allow easy resizing of shapes.

        shape_width = 20
        # Draw a rectangle of the same size of screen
        x = self.padding
        self.padding = self.padding + 1
        if self.padding > 10:
            self.padding = 0

        try:
            #canvas.rectangle(self.oledDevice.bounding_box, outline=255, fill=0)
            # Move left to right keeping track of the current x position for drawing shapes.
            canvas.text((self.oldX, self.oldY), self.oldText, font= self.font, fill=0)
            canvas.text((x, 20), self.Text, font= self.font, fill=255)
            self.oldX = x
            self.oldY = 20
            self.oldText = self.Text
            # draw.text((x, top + 20), 'Test!', font= self.font, fill=255)
        except IOError:
            print "failed"

    def display_cycle(self):
        displayLock.acquire()
        if self.oledDeviceIntialized is True:
            with self.oledCanvas as canvas:
                try:
                    self.draw_test(canvas)
                except IOError:
                    print "failed"

        displayLock.release()

        self.displayThr = threading.Timer(1, Worker.display_cycle, [self])
        self.displayThr.start()

    def cancel(self):
        print "shutdown worker ..."
        if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            self.displayThr.cancel()

        if self.pmuBusIntialized is True:
            self.pmuBus.close()

worker = Worker()
worker.run()
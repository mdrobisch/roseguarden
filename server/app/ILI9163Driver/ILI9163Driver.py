#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
#   (1) Based on the ILI9163 Library of BLavery https://github.com/BLavery/LIBtft144
#   (2) Which based on ILI9163 128x128 LCD library   - parallel I/O AVR C code
#      Copyright (C) 2012 Simon Inns    Email: simon.inns@gmail.com
#      http://www.waitingforfriday.com/index.php/Reverse_Engineering_a_1.5_inch_Photoframe
#   (3) ... then based on Antares python/parallel Raspberry Pi code:
#      http://www.raspberrypi.org/forums/viewtopic.php?t=58291&p=450201
#   (4) ... making this version lib_tft144 python SPI interface for RPI or Virtual GPIO
#      (It's looking a bit different now from Inns' original!)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


# 128x128 pixels,
# Note the board is write-only. There is no feedback if board is absent or misbehaving.

import sys

if __name__ == '__main__':
    print (sys.argv[0], 'is an importable module:')
    print ("...  from", sys.argv[0], "import TFT144")
    exit()

from time import sleep
import os
GPIO = None

TFTWIDTH    = 130
TFTHEIGHT   = 131

#ILI9163 commands
NOP=0x00
SOFT_RESET=0x01
ENTER_SLEEP_MODE=0x10
EXIT_SLEEP_MODE=0x11
ENTER_PARTIAL_MODE=0x12
ENTER_NORMAL_MODE=0x13
EXIT_INVERT_MODE=0x20
ENTER_INVERT_MODE=0x21
SET_GAMMA_CURVE=0x26
SET_DISPLAY_OFF=0x28
SET_DISPLAY_ON=0x29
SET_COLUMN_ADDRESS=0x2A
SET_PAGE_ADDRESS=0x2B
WRITE_MEMORY_START=0x2C
SET_PARTIAL_AREA=0x30
SET_SCROLL_AREA=0x33
SET_ADDRESS_MODE=0x36
SET_SCROLL_START=0X37
EXIT_IDLE_MODE=0x38
ENTER_IDLE_MODE=0x39
SET_PIXEL_FORMAT=0x3A
WRITE_MEMORY_CONTINUE=0x3C
READ_MEMORY_CONTINUE=0x3E
FRAME_RATE_CONTROL1=0xB1
FRAME_RATE_CONTROL2=0xB2
FRAME_RATE_CONTROL3=0xB3
DISPLAY_INVERSION=0xB4
POWER_CONTROL1=0xC0
POWER_CONTROL2=0xC1
POWER_CONTROL3=0xC2
POWER_CONTROL4=0xC3
POWER_CONTROL5=0xC4
VCOM_CONTROL1=0xC5
VCOM_CONTROL2=0xC6
VCOM_OFFSET_CONTROL=0xC7
POSITIVE_GAMMA_CORRECT=0xE0
NEGATIVE_GAMMA_CORRECT=0xE1
GAM_R_SEL=0xF2

VIRTUALGPIO = 0

class ILI9163Driver:
    # red board is built 180 rotated relative to black board !!
    ORIENTATION0=0
    ORIENTATION90=96
    ORIENTATION270=160
    ORIENTATION180=192
    # Do you rotate the image, or the device?  :-)

    def __init__(self, gpio, spidev, CE, dc_pin, rst_pin=0, led_pin=0, orientation=ORIENTATION0, isRedBoard=False, spi_speed=16000000):
        # CE is 0 or 1 for RPI, but is actual CE pin for virtGPIO
        # RST pin.  0  means soft reset (but reset pin still needs holding high (3V)
        # LED pin, may be tied to 3V (abt 14mA) or used on a 3V logic pin (abt 7mA)
        # and this object needs to be told the GPIO and SPIDEV objects to talk to
        global GPIO
        GPIO = gpio
        self.SPI = spidev
        self.orientation = orientation
        self.is_redboard = isRedBoard
        self.BLUE = self.colour565(0,0,255)
        self.GREEN = self.colour565(0,255, 0)
        self.RED = self.colour565(255,0,0)
        self.PINK = self.colour565(255,120,120)
        self.LIGHTBLUE = self.colour565(120,120,255)
        self.LIGHTGREEN = self.colour565(120,255,120)
        self.BLACK = self.colour565(0,0,0)
        self.WHITE = self.colour565(255,255,255)
        self.GREY = self.colour565(120,120,120)
        self.YELLOW = self.colour565(255,255,0)
        self.MAGENTA = self.colour565(255,0,255)
        self.CYAN = self.colour565(0,255,255)

        self.RST = rst_pin
        self.DC = dc_pin
        self.LED = led_pin
        GPIO.setup(dc_pin, GPIO.OUT)
        GPIO.output(dc_pin, GPIO.HIGH)
        if rst_pin:
            GPIO.setup(rst_pin, GPIO.OUT)
            GPIO.output(rst_pin, GPIO.HIGH)
        if led_pin:
            GPIO.setup(led_pin, GPIO.OUT)
            self.led_on(True)
        self.SPI.open(0, CE)    # CE is 0 or 1   (means pin CE0 or CE1) or actual CE pin for virtGPIO
        self.SPI.max_speed_hz=spi_speed
        # Black board may cope with 32000000 Hz. Red board up to 16000000. YMMV.
        sleep(0.5)
        self.init_LCD(orientation)

    def led_on(self, onoff):
        if self.LED:
            GPIO.output(self.LED, GPIO.HIGH if onoff else GPIO.LOW)

    #function to pack 3 bytes of rgb value in 2 byte integer, R,G and B 0-255
    def colour565(self, r,g,b):
       return ((b & 0xF8) << 8) | ((g & 0xFC) << 3) | (r >> 3)

    #functions to translate x,y pixel coords. to text column,row
    def textX(self, x, font=3):
       return x*(self.fontDim[font][0])

    def textY(self, y, font=3):
       return y*(self.fontDim[font][1])

    #initial LCD reset
    def reset_LCD(self):
       if self.RST == 0:
           self.write_command(SOFT_RESET)
       else:
           GPIO.output(self.RST,False)
           sleep (0.2)
           GPIO.output(self.RST,True)
       sleep (0.2)
       return

    #write command to controller
    def write_command(self, address):
       GPIO.output(self.DC,False)
       self.SPI.writebytes([address])


    #write data
    def write_data(self, data):
       GPIO.output(self.DC,True)
       if not type(data) == type([]):   # is it already a list?
            data = [data]
       self.SPI.writebytes(data)

    #-------------------------------------------

    def init_LCD(self, orientation):
       self.reset_LCD()
       self.write_command(EXIT_SLEEP_MODE)
       sleep(0.05)
       self.write_command(SET_PIXEL_FORMAT)
       self.write_data(0x05)
       self.write_command(SET_GAMMA_CURVE)
       self.write_data(0x04)
       self.write_command(GAM_R_SEL)
       self.write_data(0x01)

       self.write_command(POSITIVE_GAMMA_CORRECT)
       self.write_data([0x3f, 0x25, 0x1c, 0x1e, 0x20, 0x12, 0x2a, 0x90, 0x24, 0x11, 0, 0, 0, 0, 0])

       self.write_command(NEGATIVE_GAMMA_CORRECT)
       self.write_data([0x20, 0x20, 0x20, 0x20, 0x05, 0, 0x15, 0xa7, 0x3d, 0x18, 0x25, 0x2a, 0x2b, 0x2b, 0x3a])
       self.write_command(FRAME_RATE_CONTROL1)
       self.write_data([0x08, 0x08])

       self.write_command(DISPLAY_INVERSION)
       self.write_data(0x01)

       self.write_command(POWER_CONTROL1)
       self.write_data([0x0a, 0x02])

       self.write_command(POWER_CONTROL2)
       self.write_data(0x02)

       self.write_command(VCOM_CONTROL1)
       self.write_data([0x50, 0x5b])

       self.write_command(VCOM_OFFSET_CONTROL)
       self.write_data(0x40)
       self.set_frame()

       self.write_command(SET_ADDRESS_MODE)
       self.write_data(orientation)

       self.clear_display(self.BLACK)
       self.write_command(SET_DISPLAY_ON)
    #   self.write_command(WRITE_MEMORY_START)

    # clear display,writes same color pixel in all screen
    def clear_display(self, color):
       color_hi=color>>8
       color_lo= color&(~(65280))
       self.set_frame()
       self.write_command(WRITE_MEMORY_START)
       if GPIO.RPI_REVISION == VIRTUALGPIO:
           GPIO.output(self.DC,True)
           self.SPI.fill(16384, color)
           # For virtGPIO "fill" is MUCH faster, but is a special VirtGPIO function
       else:
           # Otherwise (RPI) repetitively push out all those identical pixels
           for row in range(TFTHEIGHT):
                self.write_data([color_hi, color_lo] * TFTWIDTH)

    def set_frame(self, x1=0, x2=TFTWIDTH-1, y1=0, y2=TFTHEIGHT-1 ):
        if self.is_redboard:
           if self.orientation==self.ORIENTATION0:
               y1 += 32
               y2 += 32
           if self.orientation==self.ORIENTATION90:
               x1 += 32
               x2 += 32
        self.write_command(SET_COLUMN_ADDRESS)
        self.write_data([0, x1, 0, x2])
        self.write_command(SET_PAGE_ADDRESS)
        self.write_data([0, y1, 0, y2])

    # draw a dot in x,y with 'color' colour
    def draw_dot(self, x,y,color):
       color_hi=color>>8
       color_lo= color&(~(65280))
       self.set_frame(x, x+1, y, y+1)
       self.write_command(WRITE_MEMORY_START)
       self.write_data([color_hi,color_lo])

    # Bresenham's algorithm to draw a line with integers
    # x0<=x1, y0<=y1
    def draw_line(self, x0,y0,x1,y1,color):
       dy=y1-y0
       dx=x1-x0
       if (dy<0):
          dy=-dy
          stepy=-1
       else:
          stepy=1
       if (dx<0):
          dx=-dx
          stepx=-1
       else:
          stepx=1
       dx <<=1
       dy <<=1
       self.draw_dot(x0,y0,color)
       if (dx>dy):
          fraction=dy-(dx>>1)
          while (x0!=x1):
             if (fraction>=0):
                y0 +=stepy
                fraction -=dx
             x0 +=stepx
             fraction +=dy
             self.draw_dot(x0,y0,color)
       else:
          fraction=dx-(dy>>1)
          while (y0!=y1):
             if (fraction>=0):
                x0 +=stepx
                fraction -=dy
             y0 +=stepy
             fraction +=dx
             self.draw_dot(x0,y0,color)

    # draws hollow rectangle
    # x0<=x1, y0<= y1
    def draw_rectangle(self, x0,y0,x1,y1,color):
       self.draw_line(x0,y0,x0,y1,color)
       self.draw_line(x0,y1,x1,y1,color)
       self.draw_line(x1,y0,x1,y1,color)
       self.draw_line(x0,y0,x1,y0,color)

    # draws filled rectangle, fills frame memory section with same pixel
    # x0<=x1, y0<=y1
    def draw_filled_rectangle(self, x0,y0,x1,y1,color):
       color_hi=color>>8
       color_lo= color&(~(65280))
       self.set_frame(x0, x1, y0, y1)

       self.write_command(WRITE_MEMORY_START)
       for pixels in range (0,(1+x1-x0)):
            dbuf = [color_hi, color_lo] * (y1-y0)
            self.write_data(dbuf)

    #Bresenham's circle algorithm, circle can't pass screen boundaries
    def draw_circle(self, x0,y0,radio,color):
       error=1-radio
       errorx=1
       errory=-2*radio
       y=radio
       x=0
       self.draw_dot(x0,y0+radio,color)
       self.draw_dot(x0,y0-radio,color)
       self.draw_dot(x0+radio,y0,color)
       self.draw_dot(x0-radio,y0,color)
       while (x<y):
          if (error>=0):
             y -=1
             errory +=2
             error +=errory
          x +=1
          errorx +=2
          error +=errorx
          self.draw_dot(x0+x,y0+y,color)
          self.draw_dot(x0-x,y0+y,color)
          self.draw_dot(x0+x,y0-y,color)
          self.draw_dot(x0-x,y0-y,color)
          self.draw_dot(x0+y,y0+x,color)
          self.draw_dot(x0-y,y0+x,color)
          self.draw_dot(x0+y,y0-x,color)
          self.draw_dot(x0-y,y0-x,color)


    def draw_image(self, image,x0=0,y0=0):
        pix = image.load()
        w = image.size[0]
        h = image.size[1]
        self.set_frame(x0, x0 + w - 1, y0, y0 + h - 1)
        self.write_command(WRITE_MEMORY_START)
        for y in range(h):
            dbuf = [0] * (w * 2)
            for x in range(w):
                pixel = pix[x, y]
                r = pixel[0]
                g = pixel[1]
                b = pixel[2]
                RGB = self.colour565(r, g, b)
                # RGB = self.YELLOW
                dbuf[2 * x] = RGB >> 8
                dbuf[1 + (2 * x)] = RGB & (~65280)
            self.write_data(dbuf)

        return True

    def draw_bmp(self, filename, x0=0, y0=0):
        if not os.path.exists(filename):
            return False
        with open(filename, 'rb') as bitmap_file:
            bitmap_file.seek(18)
            w = ord(bitmap_file.read(1))
            bitmap_file.seek(22)
            h = ord(bitmap_file.read(1))
            bitmap_file.seek(10)
            start = ord(bitmap_file.read(1))
            bitmap_file.seek(start)
            self.set_frame(x0, x0+w-1, y0, y0+h-1)
            self.write_command(WRITE_MEMORY_START)
            for y in range(h):   # 3 bytes of colour / pixel
                  dbuf = [0] * (w*2)
                  for x in range(w):
                      b = ord(bitmap_file.read(1))
                      g = ord(bitmap_file.read(1))
                      r = ord(bitmap_file.read(1))
                      RGB = self.colour565(r, g, b)
                      #RGB = self.YELLOW
                      dbuf[2*x] = RGB>>8
                      dbuf[1 + (2*x)] = RGB&(~65280)
                  self.write_data(dbuf)
                  # Now, BMP has a 4byte alignment issue at end of each line   V1.0.1
                  x = 3*w # bytes in line @ 3bytes/pixel
                  while (x % 4):
                      x += 1
                      bitmap_file.read(1)   # waste a byte until aligned
        return True

    def invert_screen(self):
       self.write_command(ENTER_INVERT_MODE)

    def normal_screen(self):
       self.write_command(EXIT_INVERT_MODE)


########################################################################

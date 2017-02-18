import RPi.GPIO as GPIO
from ILI9163Driver import ILI9163Driver
from time import sleep
import spidev

from PIL import ImageFont, ImageDraw, Image
image = Image.new("RGB", (130, 131), "white")

draw = ImageDraw.Draw(image)

# use a truetype font
font = ImageFont.load_default()

draw.text((20, 25), "Hallo Schoeni", font=font, fill=(255,0,0,255))
draw.text((20, 45), "Hallo Schoeni", font=font, fill=(255,0,0,255))

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

RST = 18
CE =   0    # 0 or 1 for CE0 / CE1 number (NOT the pin#)
DC =  22    # Labeled on board as "A0"
LED = 23    # LED backlight sinks 10-14 mA @ 3V


# Don't forget the other 2 SPI pins SCK and MOSI (SDA)

TFT = ILI9163Driver(GPIO, spidev.SpiDev(), CE, DC, RST, LED, isRedBoard=False,spi_speed=100000)
from PIL import Image
im = Image.open("heart.png")

TFT.clear_display(TFT.WHITE)

TFT.draw_image(im, 20, 20)
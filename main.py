import board
import busio
import digitalio
import adafruit_dotstar
import time

#import adafruit_fancyled as fancy

# One pixel connected internally!
dot = adafruit_dotstar.DotStar(board.APA102_SCK,
                               board.APA102_MOSI,
                               1,
                               brightness=0.2)

strip = adafruit_dotstar.DotStar(board.SCK,
                                 board.MOSI,
                                 1,
                                 brightness=0.2)

# # Built in red LED
led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT


dot[0] = (255,0,111)

i = 0
while True:

    strip[0] = (i,0,0)

    i = (i+1) % 256  # run from 0 to 255
    time.sleep(0.01) # make bigger to slow down

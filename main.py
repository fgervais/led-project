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

# spi = busio.SPI(board.SCK, MISO=board.MISO)

# # Built in red LED
# led = digitalio.DigitalInOut(board.D13)
# led.direction = digitalio.Direction.OUTPUT

######################### HELPERS ##############################

# Helper to give us a nice color swirl
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if (pos < 0):
        return (0, 0, 0)
    if (pos > 255):
        return (0, 0, 0)
    if (pos < 85):
        return (int(pos * 3), int(255 - (pos*3)), 0)
    elif (pos < 170):
        pos -= 85
        return (int(255 - pos*3), 0, int(pos*3))
    else:
        pos -= 170
        return (0, int(pos*3), int(255 - pos*3))

######################### MAIN LOOP ##############################

# while not spi.try_lock():
#     pass

# spi.configure(baudrate=5000000, phase=0, polarity=0)

dot[0] = (255,0,111)

i = 0
while True:
    # spin internal LED around!
    dot[0] = (255,0,111)

    #spi.write(bytes([0x01, 0xFF]))

    i = (i+1) % 256  # run from 0 to 255
    time.sleep(0.01) # make bigger to slow down

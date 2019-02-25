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

i2c = busio.I2C(board.SCL, board.SDA)

# # Built in red LED
led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT


dot[0] = (255,0,111)



while not i2c.try_lock():
    pass

i = 0
while True:

    print("I2C addresses found:", [hex(device_address)
                                   for device_address in i2c.scan()])

    strip[0] = (i,0,0)

    i = (i+1) % 256  # run from 0 to 255
    time.sleep(0.01) # make bigger to slow down

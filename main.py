import board
import busio
import digitalio
import adafruit_dotstar
import time

import adafruit_fancyled as fancy

from adafruit_bus_device.i2c_device import I2CDevice

# https://www.tindie.com/products/Saimon/i2cencoder-v2-connect-multiple-encoder-on-i2c-bus/?pt=ac_prod_search
class I2CEncoderV2():
    def __init__(self, device, illuminated=False):
        self.device = device

        if illuminated:
            self.config = (0x01 << 5)
        else:
            self.config = 0x00

    def read(self, register, length):
        result = bytearray(length)

        with self.device:
            self.device.write(bytes([register]), stop=False)
            self.device.readinto(result)

        return int.from_bytes(result, 'big')

    def write(self, register, data):
        with self.device:
            self.device.write(bytes([register]) + data)

    @property
    def config(self):
        return self.read(0x00, 1)

    @config.setter
    def config(self, value):
        self.write(0x00, bytes([value]))

    @property
    def status(self):
        return self.read(0x05, 1)

    @property
    def counter_value(self):
        return self.read(0x08, 4)

    @property
    def counter_max_value(self):
        return self.read(0x0c, 4)

    @counter_max_value.setter
    def counter_max_value(self, value):
        self.write(0x0c, value.to_bytes(4, 'big'))


    @property
    def color(self):
        r = self.read(0x18, 1)
        g = self.read(0x19, 1)
        b = self.read(0x1a, 1)

        return fancy.CRGB(r, g, b)

    @color.setter
    def color(self, color):
        if type(color) is fancy.CHSV:
            color = fancy.CRGB(color)

        self.write(0x18, color.pack().to_bytes(3, 'big'))


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
device1 = I2CDevice(i2c, 0x01)
# device2 = I2CDevice(i2c, 0x02)
encoder = I2CEncoderV2(device1, illuminated=True)
# encoder2 = I2CEncoderV2(device2)

encoder.counter_max_value = 255
# print(encoder.counter_max_value)

# # Built in red LED
led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT


dot[0] = (255,0,111)
color1 = fancy.CHSV(0.08, 1.0, 1.0)
print(color1.pack())
encoder.color = color1

# while not i2c.try_lock():
#     pass

i = 0
while True:

    # print("I2C addresses found:", [hex(device_address)
    #                                for device_address in i2c.scan()])

    print("Hello")
    print("ENCODER CONFIG: " + hex(encoder.config))
    print("ENCODER STATUS: " + hex(encoder.status))
    print("COUNTER VALUE: " + hex(encoder.counter_value))
    print("COUNTER MAX VALUE: " + hex(encoder.counter_max_value))
    # print("test: " + str(encoder2.counter_value))

    print(encoder.color)

    strip[0] = (i,0,0)

    i = (i+1) % 256  # run from 0 to 255
    time.sleep(1) # make bigger to slow down

import board
import busio
import digitalio
import adafruit_dotstar
import time

import adafruit_fancyled as fancy

from adafruit_bus_device.i2c_device import I2CDevice

# https://www.tindie.com/products/Saimon/i2cencoder-v2-connect-multiple-encoder-on-i2c-bus/?pt=ac_prod_search
class I2CEncoderV2():
    def __init__(self, device, name="", wrap=False, illuminated=False):
        self.device = device
        self.name = name

        config = 0x00
        if illuminated:
            self.config |= (0x01 << 5)
        if wrap:
            self.config |= (0x01 << 1)

    def __str__(self):
        s  = "ENC[{}]: config: \t\t{}\n".format(self.name, hex(self.config))
        s += "ENC[{}]: status: \t\t{}\n".format(self.name, hex(self.status))
        s += "ENC[{}]: counter_value: \t{}\n".format(self.name,
                                                  hex(self.counter_value))
        s += "ENC[{}]: counter_max_value: \t{}\n".format(self.name,
                                                  hex(self.counter_max_value))
        s += "ENC[{}]: color: \t\t{}\n".format(self.name, self.color)

        return s

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

i2c_bus = busio.I2C(board.SCL, board.SDA)

i2c_devices = []
i2c_devices.append(I2CDevice(i2c_bus, 0x01))
i2c_devices.append(I2CDevice(i2c_bus, 0x02))

hue_encoder = I2CEncoderV2(i2c_devices[0],
                           "hue",
                           wrap=True,
                           illuminated=True)
value_encoder = I2CEncoderV2(i2c_devices[1],
                             "value",
                             wrap=True,
                             illuminated=True)


dot[0] = (255,0,111)


for i in [hue_encoder, value_encoder]:
    i.counter_max_value = 255
    i.color = fancy.CHSV(0)

# # Built in red LED
led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT



while True:
    print("Hello")
    for i in [hue_encoder, value_encoder]:
        print(i)


    hue_encoder.color = fancy.CHSV(hue_encoder.counter_value)


    # strip[0] = (i,0,0)

    # i = (i+1) % 256  # run from 0 to 255
    time.sleep(1) # make bigger to slow down

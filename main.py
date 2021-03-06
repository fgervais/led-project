import board
import busio
import digitalio
import adafruit_dotstar
import time

import adafruit_fancyled as fancy

from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_fancyled import CRGB, CHSV


DOTSTAR_MAX_BRIGHTNESS = 0.2
DEBUG = False


# https://www.tindie.com/products/Saimon/i2cencoder-v2-connect-multiple-encoder-on-i2c-bus/?pt=ac_prod_search
class I2CEncoderV2():
    def __init__(self, device, name="", wrap=False, illuminated=False):
        self.device = device
        self.name = name

        config = 0x00
        if illuminated:
            config |= (0x01 << 5)
        if wrap:
            config |= (0x01 << 1)
        self.config = config

        self.last_set_color = CRGB(0, 0, 0)
        self.fast_mode = False

    def __str__(self):
        s  = "ENC[{}]: config: \t{}\n".format(self.name, hex(self.config))
        s += "ENC[{}]: status: \t{}\n".format(self.name, hex(self.status))
        s += "ENC[{}]: value: \t{}\n".format(self.name,
                                                  hex(self.value))
        s += "ENC[{}]: max_value: \t{}\n".format(self.name,
                                                  hex(self.max_value))
        s += "ENC[{}]: color: \t{}\n".format(self.name, self.color)

        return s

    def read(self, register, length):
        result = bytearray(length)

        with self.device:
            while True:
                try:
                    self.device.write(bytes([register]), stop=False)
                    self.device.readinto(result)
                    break
                except:
                    print("---------------")
                    print("ERROR: I2C READ")
                    print("---------------")
                    time.sleep(0.1)

        return int.from_bytes(result, 'big')

    def write(self, register, data):
        with self.device:
            while True:
                try:
                    self.device.write(bytes([register]) + data)
                    break
                except:
                    print("----------------")
                    print("ERROR: I2C WRITE")
                    print("----------------")
                    time.sleep(0.1)

    def toggle_fast_mode(self):
        if self.fast_mode:
            self.increment_step = 1
            self.fast_mode = False
        else:
            self.increment_step = 10
            self.fast_mode = True

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
    def value(self):
        return self.read(0x08, 4)

    @property
    def max_value(self):
        return self.read(0x0c, 4)

    @max_value.setter
    def max_value(self, value):
        self.write(0x0c, value.to_bytes(4, 'big'))

    @property
    def increment_step(self):
        return self.read(0x14, 4)

    @increment_step.setter
    def increment_step(self, value):
        self.write(0x14, value.to_bytes(4, 'big'))

    @property
    def color(self):
        r = self.read(0x18, 1)
        g = self.read(0x19, 1)
        b = self.read(0x1a, 1)

        return CRGB(r, g, b)

    @color.setter
    def color(self, color):
        if type(color) is CHSV:
            color = CRGB(color)

        if repr(color) != repr(self.last_set_color):
            debug("ENC[{}]: \tcolor: \t\t{}".format(self.name, color))
            self.write(0x18, color.pack().to_bytes(3, 'big'))
            self.last_set_color = color


class LedStrip():
    def __init__(self, dotstar, name=""):
        self.dotstar = dotstar
        self.name = name

        self.last_set_color = CRGB(0, 0, 0)
        self.last_set_brightness = 1.0

    def toggle_brightness(self):
        if self.dotstar.brightness == 0:
            self.dotstar.brightness = (DOTSTAR_MAX_BRIGHTNESS *
                                       self.last_set_brightness)
        else:
            self.dotstar.brightness = 0

    @property
    def color(self):
        return self.last_set_color

    @color.setter
    def color(self, color):
        if type(color) is CHSV:
            color = CRGB(color)

        if repr(color) != repr(self.last_set_color):
            debug("STRIP[{}]: \tcolor: \t\t{}".format(self.name, color))
            self.dotstar[0] = color.pack()
            self.last_set_color = color

    @property
    def brightness(self):
        return self.last_set_brightness

    @brightness.setter
    def brightness(self, value):
        if value != self.last_set_brightness:
            debug("STRIP[{}]: \tbrightness: \t{}".format(self.name, value))
            self.dotstar.brightness = DOTSTAR_MAX_BRIGHTNESS * value
            self.last_set_brightness = value


def debug(message):
    if DEBUG:
        print(message)


# One pixel connected internally!
dot = adafruit_dotstar.DotStar(board.APA102_SCK,
                               board.APA102_MOSI,
                               1,
                               brightness=DOTSTAR_MAX_BRIGHTNESS)

# strip = adafruit_dotstar.DotStar(board.SCK,
#                                  board.MOSI,
#                                  1,
#                                  brightness=DOTSTAR_MAX_BRIGHTNESS)

i2c_bus = busio.I2C(board.SCL, board.SDA, frequency=100000)

i2c_devices = []
i2c_devices.append(I2CDevice(i2c_bus, 0x01))
i2c_devices.append(I2CDevice(i2c_bus, 0x02))

hue_encoder = I2CEncoderV2(i2c_devices[0],
                           "hue",
                           wrap=True,
                           illuminated=True)
value_encoder = I2CEncoderV2(i2c_devices[1],
                             "value",
                             wrap=False,
                             illuminated=True)


strip = LedStrip(dot, name="wall")


for i in [hue_encoder, value_encoder]:
    i.max_value = 255
    i.color = CHSV(0)
    i.toggle_fast_mode()

# Built in red LED
led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT

for i in [hue_encoder, value_encoder]:
    print(i)

while True:
    desired_color = fancy.gamma_adjust(CHSV(hue_encoder.value))

    hue_encoder.color = desired_color
    strip.color = desired_color

    if hue_encoder.status & (0x01 << 1):
        debug("toggle fast mode")
        hue_encoder.toggle_fast_mode()

    value = value_encoder.value
    value_encoder.color = CRGB(value, value, value)
    strip.brightness = value / 255

    if value_encoder.status & (0x01 << 1):
        debug("toggle brightness")
        strip.toggle_brightness()


    # time.sleep(0.1) # make bigger to slow down

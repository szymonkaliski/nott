import digitalio
import busio

from adafruit_neotrellis.multitrellis import MultiTrellis
from adafruit_neotrellis.neotrellis import NeoTrellis
from board import SCL, SDA, D5


class Trellis(object):
    def __init__(self):
        # setup trellis
        i2c_bus = busio.I2C(SCL, SDA)
        self.trellis = MultiTrellis(
            [
                [
                    NeoTrellis(i2c_bus, True, addr=0x31),
                    NeoTrellis(i2c_bus, True, addr=0x30),
                    NeoTrellis(i2c_bus, True, addr=0x2F),
                    NeoTrellis(i2c_bus, True, addr=0x2E),
                ],
                [
                    NeoTrellis(i2c_bus, True, addr=0x35),
                    NeoTrellis(i2c_bus, True, addr=0x34),
                    NeoTrellis(i2c_bus, True, addr=0x33),
                    NeoTrellis(i2c_bus, True, addr=0x32),
                ],
            ]
        )

        # interrupt pin - sync only when needed
        self.interrupt = digitalio.DigitalInOut(D5)
        self.interrupt.direction = digitalio.Direction.INPUT

    def update(self):
        if self.interrupt.value is False:
            self.trellis.sync()

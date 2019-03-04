import time

from board import SCL, SDA
import busio

from adafruit_neotrellis.neotrellis import NeoTrellis
from adafruit_neotrellis.multitrellis import MultiTrellis

i2c_bus = busio.I2C(SCL, SDA)

trellis = MultiTrellis(
    [
        [
            NeoTrellis(i2c_bus, False, addr=0x31),
            NeoTrellis(i2c_bus, False, addr=0x30),
            NeoTrellis(i2c_bus, False, addr=0x2F),
            NeoTrellis(i2c_bus, False, addr=0x2E),
        ],
        [
            NeoTrellis(i2c_bus, False, addr=0x35),
            NeoTrellis(i2c_bus, False, addr=0x34),
            NeoTrellis(i2c_bus, False, addr=0x33),
            NeoTrellis(i2c_bus, False, addr=0x32),
        ],
    ]
)

OFF = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
ORANGE = (255, 120, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
WHITE = (255, 255, 255)


def led_test():
    trellis.color(0, 0, RED)
    trellis.color(4, 0, BLUE)
    trellis.color(8, 0, GREEN)
    trellis.color(12, 0, CYAN)
    trellis.color(0, 4, YELLOW)
    trellis.color(4, 4, PURPLE)
    trellis.color(8, 4, WHITE)
    trellis.color(12, 4, ORANGE)


for x in range(16):
    for y in range(8):
        trellis.color(x, y, OFF)

while True:
    led_test()
    trellis.sync()
    time.sleep(0.02)

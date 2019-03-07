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


COLOR_OFF = (0, 0, 0)
COLOR_RED = (200, 0, 0)
COLOR_RED_MUTED = (10, 0, 0)
COLOR_GREEN = (0, 200, 0)
COLOR_GREEN_MUTED = (0, 10, 0)


class Row(object):
    mode = "play"
    is_recording = False
    is_playing = False
    index = None
    trellis = None

    def __init__(self, index, trellis):
        self.index = index
        self.trellis = trellis

        for x in range(16):
            self.set_color(x, COLOR_OFF)

            self.trellis.activate_key(x, self.index, NeoTrellis.EDGE_RISING)
            self.trellis.activate_key(x, self.index, NeoTrellis.EDGE_FALLING)
            self.trellis.set_callback(x, self.index, self.on_click)

    def set_color(self, x, color):
        self.trellis.color(x, self.index, color)

    def on_click(self, x, _, edge):
        print(self.index, x, edge)

        if edge == NeoTrellis.EDGE_RISING and x == 0:
            self.is_recording = not self.is_recording

        if edge == NeoTrellis.EDGE_RISING and x == 1:
            self.is_playing = not self.is_playing

    def draw(self):
        self.set_color(0, COLOR_RED if self.is_recording else COLOR_RED_MUTED)
        self.set_color(1, COLOR_GREEN if self.is_playing else COLOR_GREEN_MUTED)


rows = list(map(lambda i: Row(i, trellis), range(8)))

print("initied!")

while True:
    for row in rows:
        row.draw()
    trellis.sync()
    time.sleep(0.02)

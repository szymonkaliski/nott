import busio
import liblo
import signal
import sys
import time

from adafruit_neotrellis.multitrellis import MultiTrellis
from adafruit_neotrellis.neotrellis import NeoTrellis
from board import SCL, SDA
from enum import Enum

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

CHUCK_HOST = "127.0.0.1"
CHUCK_IN_PORT = 9998
CHUCK_OUT_PORT = 9999

chuck_in = liblo.Server(CHUCK_IN_PORT)
chuck_out = liblo.Address(CHUCK_HOST, CHUCK_OUT_PORT)


class COLOR(object):
    OFF = (0, 0, 0)
    RED = (200, 0, 0)
    RED_MUTED = (10, 0, 0)
    GREEN = (0, 200, 0)
    GREEN_MUTED = (0, 10, 0)


class MODE(Enum):
    PLAY = 1


class Row(object):
    mode = MODE.PLAY

    is_recording = False
    is_playing = False
    index = None

    trellis = None
    chuck_out = None

    def __init__(self, index, trellis, chuck_in, chuck_out):
        self.index = index
        self.trellis = trellis

        self.chuck_in = chuck_in  # TODO chuck_in.add_method for self
        self.chuck_out = chuck_out

        self.clear()

        for x in range(16):
            self.trellis.activate_key(x, self.index, NeoTrellis.EDGE_RISING)
            self.trellis.activate_key(x, self.index, NeoTrellis.EDGE_FALLING)
            self.trellis.set_callback(x, self.index, self.on_click)

    def clear(self):
        for x in range(16):
            self.set_color(x, COLOR.OFF)

    def set_color(self, x, color):
        self.trellis.color(x, self.index, color)

    def to_chuck(self, path, value):
        liblo.send(self.chuck_out, path, value)

    def on_click(self, x, _, edge):
        print(self.index, x, edge)

        if edge == NeoTrellis.EDGE_RISING and x == 0:
            self.is_recording = not self.is_recording
            self.to_chuck("/rec", self.is_recording)

        if edge == NeoTrellis.EDGE_RISING and x == 1:
            self.is_playing = not self.is_playing

    def draw(self):
        if self.mode == MODE.PLAY:
            self.set_color(0, COLOR.RED if self.is_recording else COLOR.RED_MUTED)
            self.set_color(1, COLOR.GREEN if self.is_playing else COLOR.GREEN_MUTED)


rows = list(map(lambda i: Row(i, trellis, chuck_in, chuck_out), range(8)))


def chuck_in_fallback(path, args, types, src):
    print("unknown message '%s' from '%s'" % (path, src.url))

    for a, t in zip(args, types):
        print("argument of type '%s': %s" % (t, a))


chuck_in.add_method(None, None, chuck_in_fallback)


def signal_handler(signal, frame):
    for row in rows:
        row.clear()
    sys.exit(0)


# handle exit gracefully
signal.signal(signal.SIGINT, signal_handler)

print("initied!")

while True:
    for row in rows:
        row.draw()

    trellis.sync()
    chuck_in.recv(0)

    time.sleep(0.01)

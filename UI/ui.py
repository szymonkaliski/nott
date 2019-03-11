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
CHUCK_IN_PORT = 3001
CHUCK_OUT_PORT = 3000

chuck_in = liblo.ServerThread(CHUCK_IN_PORT)
chuck_out = liblo.Address(CHUCK_HOST, CHUCK_OUT_PORT)


class COLOR(object):
    OFF = (0, 0, 0)
    RED = (200, 0, 0)
    RED_MUTED = (10, 0, 0)
    GREEN = (0, 200, 0)
    GREEN_MUTED = (0, 10, 0)
    BLUE_MUTED = (0, 0, 10)
    WHITE_MUTED = (3, 2, 0)


class MODE(Enum):
    PLAY = 1


class Row(object):
    mode = MODE.PLAY

    is_recording = False
    is_playing = False
    id = None
    playback_pos = 0.0

    trellis = None
    chuck_out = None

    def __init__(self, id, trellis, chuck_in, chuck_out):
        self.id = id
        self.trellis = trellis

        self.chuck_in = chuck_in  # TODO chuck_in.add_method for self
        self.chuck_out = chuck_out

        self.clear()

        for x in range(16):
            self.trellis.activate_key(x, self.id, NeoTrellis.EDGE_RISING)
            self.trellis.activate_key(x, self.id, NeoTrellis.EDGE_FALLING)
            self.trellis.set_callback(x, self.id, self.on_click)

    def clear(self):
        for x in range(16):
            self.set_color(x, COLOR.OFF)

    def set_color(self, x, color):
        self.trellis.color(x, self.id, color)

    def to_chuck(self, path, value):
        liblo.send(self.chuck_out, path, self.id, value)

    def on_osc_msg(self, path, args):
        if "status" in path:
            self.playback_pos = args[0]

    def on_click(self, x, _, edge):
        print(self.id, x, edge)

        if edge == NeoTrellis.EDGE_RISING and x == 0:
            self.is_recording = not self.is_recording

            if self.is_recording:
                self.is_playing = True

            self.to_chuck("/recording", 1 if self.is_recording else 0)

        if edge == NeoTrellis.EDGE_RISING and x == 1:
            self.is_playing = not self.is_playing
            self.to_chuck("/playing", 1 if self.is_playing else 0)

        if edge == NeoTrellis.EDGE_RISING and 2 <= x < 14:
            self.to_chuck("/jump", (x - 2) / (14 - 2))

    def draw(self):
        playback_pos_idx = round(self.playback_pos * (14 - 2)) + 2

        if self.mode == MODE.PLAY:
            self.set_color(0, COLOR.RED if self.is_recording else COLOR.RED_MUTED)
            self.set_color(1, COLOR.GREEN if self.is_playing else COLOR.GREEN_MUTED)

        for i in range(2, 14):
            self.set_color(i, COLOR.WHITE_MUTED if i == playback_pos_idx else COLOR.OFF)


rows = list(map(lambda i: Row(i, trellis, chuck_in, chuck_out), range(8)))


for row in rows:
    chuck_in.add_method("/status/" + str(row.id), "f", row.on_osc_msg)

chuck_in.start()


def signal_handler(signal, frame):
    for row in rows:
        row.clear()
    chuck_in.stop()
    sys.exit(0)


# handle exit gracefully
signal.signal(signal.SIGINT, signal_handler)

print("Nótt UI Ready")

while True:
    for row in rows:
        row.draw()
    trellis.sync()

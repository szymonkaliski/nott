from consts import COLOR, MODE
from adafruit_neotrellis.neotrellis import NeoTrellis

EDGE_RISING = NeoTrellis.EDGE_RISING
EDGE_FALLING = NeoTrellis.EDGE_FALLING

MODES = {0: MODE.PLAY, 1: MODE.CONTROL_1, 2: MODE.CONTROL_2}


class Topbar(object):
    mode = MODE.PLAY
    rows = []
    trellis = None

    def __init__(self, rows, trellis):
        self.rows = rows
        self.trellis = trellis

        for x in range(16):
            self.trellis.activate_key(x, 0, EDGE_RISING)
            self.trellis.activate_key(x, 0, EDGE_FALLING)
            self.trellis.set_callback(x, 0, self.on_click)

    def on_click(self, x, _, edge):
        if 0 <= x < 3 and MODES[x] != self.mode and edge == EDGE_RISING:
            self.mode = MODES[x]

            for row in self.rows:
                row.mode = self.mode

    def set_color(self, x, color):
        self.trellis.color(x, 0, color)

    def draw(self):
        for x in range(3):
            self.set_color(
                x, COLOR.WHITE if self.mode == MODES[x] else COLOR.WHITE_MUTED
            )

    def clear(self):
        for x in range(16):
            self.set_color(x, COLOR.OFF)

from consts import COLOR, MODE
from adafruit_neotrellis.neotrellis import NeoTrellis

EDGE_RISING = NeoTrellis.EDGE_RISING
EDGE_FALLING = NeoTrellis.EDGE_FALLING

MODES = {0: MODE.PLAY, 1: MODE.CONTROL_1, 2: MODE.CONTROL_2, 3: MODE.CONTROL_3}


class Topbar(object):
    mode = MODE.PLAY
    is_alt_held = False

    rows = []
    trellis = None
    patterns = None

    def __init__(self, rows, patterns, trellis):
        self.rows = rows
        self.patterns = patterns
        self.trellis = trellis

        for x in range(16):
            self.trellis.activate_key(x, 0, EDGE_RISING)
            self.trellis.activate_key(x, 0, EDGE_FALLING)
            self.trellis.set_callback(x, 0, self.on_click)

    def on_click(self, x, _, edge):
        if 0 <= x < 4 and MODES[x] != self.mode and edge == EDGE_RISING:
            self.mode = MODES[x]

            for row in self.rows:
                row.mode = self.mode

        if 8 <= x < 12 and edge == EDGE_RISING:
            if self.is_alt_held:
                self.patterns.clear_recording(x - 4)
            else:
                self.patterns.on_click(x - 4)

        if x == 15:
            self.is_alt_held = edge == EDGE_RISING

            for row in self.rows:
                row.is_alt_held = self.is_alt_held

    def set_color(self, x, color):
        self.trellis.color(x, 0, color)

    def draw(self):
        for x in range(4):
            self.set_color(
                x, COLOR.WHITE if self.mode == MODES[x] else COLOR.WHITE_MUTED
            )

        for x in range(8, 12):
            if self.patterns.is_recording or self.patterns.is_replaying:
                self.set_color(
                    x,
                    COLOR.WHITE
                    if self.patterns.active_idx == x - 4
                    else COLOR.WHITE_MUTED,
                )
            else:
                self.set_color(x, COLOR.WHITE_MUTED)

        self.set_color(15, COLOR.WHITE_MUTED if self.is_alt_held else COLOR.OFF)

    def clear(self):
        for x in range(16):
            self.set_color(x, COLOR.OFF)

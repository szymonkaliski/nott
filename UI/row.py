from adafruit_neotrellis.neotrellis import NeoTrellis

from consts import COLOR, MODE, RATES

EDGE_RISING = NeoTrellis.EDGE_RISING
EDGE_FALLING = NeoTrellis.EDGE_FALLING


class Row(object):
    # the world
    trellis = None
    chuck_out = None

    # id & row
    id = None
    rowIdx = None

    # internal state
    mode = MODE.PLAY
    held_index = -1

    # from chuck
    is_recording = False
    is_playing = False
    playback_pos = 0.0
    volume = 1.0
    feedback = 1.0
    rate = 1.0
    direction = 1
    subloop = (0.0, 1.0)

    def __init__(self, id, rowIdx, trellis, chuck_in, chuck_send_out):
        self.id = id
        self.rowIdx = rowIdx
        self.trellis = trellis

        self.chuck_in = chuck_in
        self.chuck_send_out = chuck_send_out

        self.clear()

        for x in range(16):
            self.trellis.activate_key(x, self.rowIdx, EDGE_RISING)
            self.trellis.activate_key(x, self.rowIdx, EDGE_FALLING)
            self.trellis.set_callback(x, self.rowIdx, self.on_click)

    def clear(self):
        for x in range(16):
            self.set_color(x, COLOR.OFF)

    def set_color(self, x, color):
        self.trellis.color(x, self.rowIdx, color)

    def to_chuck(self, path, *values):
        self.chuck_send_out(path, self.id, *values)

    def on_osc_msg(self, path, args):
        if "status" in path:
            self.is_playing = args[0]
            self.is_recording = args[1]
            self.playback_pos = args[2]
            self.volume = args[3]
            self.feedback = args[4]
            self.rate = args[5]
            self.direction = args[6]
            self.subloop = (args[7], args[8])

    def on_click(self, x, _, edge):
        if self.mode == MODE.PLAY:
            if edge == EDGE_RISING and 0 <= x < 16:
                is_sublooping = self.subloop[0] > 0.0 or self.subloop[1] < 1.0

                if self.held_index < 0:
                    self.held_index = x
                    self.to_chuck("/jump", x / 16)

                    if is_sublooping:
                        self.to_chuck("/subloop", 0.0, 1.0)
                else:
                    a, b = self.held_index / 16, x / 16
                    self.held_index = -1
                    self.to_chuck("/subloop", min(a, b), max(a, b))

            if edge == EDGE_FALLING and self.held_index == x:
                self.held_index = -1

        if self.mode == MODE.CONTROL_1 and edge == EDGE_RISING:
            if x == 0:
                self.to_chuck("/recording", 0 if self.is_recording else 1)

            if 1 <= x <= 7:
                self.to_chuck("/rate", RATES[x - 1])

            if x == 8:
                self.to_chuck("/direction", 1 if self.direction < 0 else -1)

            if x == 15:
                self.to_chuck("/play", 0 if self.is_playing else 1)

        if self.mode == MODE.CONTROL_2 and edge == EDGE_RISING:
            if 0 <= x <= 7:
                self.to_chuck("/volume", x / 7)

            if 8 <= x <= 16:
                self.to_chuck("/feedback", (x - 8) / 7)

    def draw(self):
        if self.mode == MODE.PLAY:
            playback_pos_idx = round(self.playback_pos * 16)
            is_sublooping = self.subloop[0] > 0.0 or self.subloop[1] < 1.0

            for i in range(0, 16):
                if i == playback_pos_idx:
                    self.set_color(
                        i, COLOR.WHITE if self.is_playing else COLOR.WHITE_MUTED
                    )
                elif i == round(self.subloop[0] * 16) and is_sublooping:
                    self.set_color(i, COLOR.WHITE_MUTED)
                elif i == round(self.subloop[1] * 16) and is_sublooping:
                    self.set_color(i, COLOR.WHITE_MUTED)
                else:
                    self.set_color(i, COLOR.OFF)

        if self.mode == MODE.CONTROL_1:
            self.set_color(0, COLOR.WHITE if self.is_recording else COLOR.WHITE_MUTED)

            for idx, rate in enumerate(RATES):
                if idx == 3:
                    self.set_color(
                        4, COLOR.WHITE if rate == self.rate else COLOR.WHITE_MUTED
                    )
                else:
                    self.set_color(
                        idx + 1, COLOR.WHITE if rate == self.rate else COLOR.OFF
                    )

            self.set_color(8, COLOR.WHITE if self.direction < 0 else COLOR.WHITE_MUTED)

            for i in range(9, 15):
                self.set_color(i, COLOR.OFF)

            self.set_color(15, COLOR.WHITE if self.is_playing else COLOR.WHITE_MUTED)

        if self.mode == MODE.CONTROL_2:
            for i in range(0, 8):
                self.set_color(
                    i, COLOR.WHITE_MUTED if i / 8 <= self.volume else COLOR.OFF
                )

            for i in range(8, 16):
                self.set_color(
                    i, COLOR.WHITE_MUTED if (i - 8) / 8 <= self.feedback else COLOR.OFF
                )

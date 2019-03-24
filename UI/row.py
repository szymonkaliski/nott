from adafruit_neotrellis.neotrellis import NeoTrellis

from consts import COLOR, MODE, PLAYBACK_MODES, RATES

EDGE_RISING = NeoTrellis.EDGE_RISING
EDGE_FALLING = NeoTrellis.EDGE_FALLING

GRANULAR_SPANS = [1.0 / 128.0, 1.0 / 64.0, 1.0 / 32.0, 1.0 / 16.0]
GRANULAR_LENGTHS = [1.0 / 128.0, 1.0 / 64.0, 1.0 / 32.0, 1.0 / 16.0]
GRANULAR_VOICES = [2, 4, 8, 16]


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
    playback_mode = None
    is_recording = False
    is_playing = False

    volume = 1.0
    feedback = 1.0

    playback_pos = 0.0
    subloop = (0.0, 1.0)

    rate = 1.0
    direction = 1

    granular_span = 0
    granular_length = 0
    granular_voices = 0
    granular_direction = 0
    granular_repitch = 0

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
        if "/status/" in path:
            self.playback_mode = args[0]
            self.is_playing = args[1]
            self.is_recording = args[2]
            self.playback_pos = args[3]
            self.volume = args[4]
            self.feedback = args[5]
            self.rate = args[6]
            self.direction = args[7]
            self.subloop = (args[8], args[9])

        if "/status_granular/" in path:
            self.granular_span = args[0]
            self.granular_length = args[1]
            self.granular_voices = args[2]
            self.granular_direction = args[3]  # 1 fwd, 2 bkwd, 3 rand
            self.granular_repitch = args[4]  # 1 on, 0 off

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

            if x == 10:
                self.to_chuck("/mode", PLAYBACK_MODES.STANDARD)

            if x == 11:
                self.to_chuck("/mode", PLAYBACK_MODES.GRANULAR)

            if x == 15:
                self.to_chuck("/play", 0 if self.is_playing else 1)

        if self.mode == MODE.CONTROL_2 and edge == EDGE_RISING:
            if 0 <= x <= 7:
                self.to_chuck("/volume", x / 7)

            if 8 <= x <= 16:
                self.to_chuck("/feedback", (x - 8) / 7)

        if self.mode == MODE.CONTROL_3 and edge == EDGE_RISING:
            if 0 <= x <= 3:
                self.to_chuck("/granular_span", GRANULAR_SPANS[x])

            if 4 <= x <= 7:
                self.to_chuck("/granular_length", GRANULAR_LENGTHS[x - 4])

            if 8 <= x <= 11:
                self.to_chuck("/granular_voices", GRANULAR_VOICES[x - 8])

            if x == 12:
                self.to_chuck("/granular_direction", 1)

            if x == 13:
                self.to_chuck("/granular_direction", 2)

            if x == 14:
                self.to_chuck("/granular_direction", 3)

            if x == 15:
                self.to_chuck(
                    "/granular_repitch", 0 if self.granular_repitch == 1 else 1
                )

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
            self.set_color(9, COLOR.OFF)

            self.set_color(
                10,
                COLOR.WHITE
                if self.playback_mode == PLAYBACK_MODES.STANDARD
                else COLOR.WHITE_MUTED,
            )

            self.set_color(
                11,
                COLOR.WHITE
                if self.playback_mode == PLAYBACK_MODES.GRANULAR
                else COLOR.WHITE_MUTED,
            )

            for i in range(12, 15):
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

        if self.mode == MODE.CONTROL_3:
            if self.playback_mode == PLAYBACK_MODES.GRANULAR:
                for i in range(0, 4):
                    self.set_color(
                        i,
                        COLOR.WHITE_MUTED
                        if GRANULAR_SPANS[i] == self.granular_span
                        else COLOR.OFF,
                    )

                for i in range(4, 8):
                    self.set_color(
                        i,
                        COLOR.WHITE_MUTED
                        if GRANULAR_LENGTHS[i - 4] == self.granular_length
                        else COLOR.OFF,
                    )

                for i in range(8, 12):
                    self.set_color(
                        i,
                        COLOR.WHITE_MUTED
                        if GRANULAR_VOICES[i - 8] == self.granular_voices
                        else COLOR.OFF,
                    )

                self.set_color(
                    12, COLOR.WHITE_MUTED if self.granular_direction == 1 else COLOR.OFF
                )
                self.set_color(
                    13, COLOR.WHITE_MUTED if self.granular_direction == 2 else COLOR.OFF
                )
                self.set_color(
                    14, COLOR.WHITE_MUTED if self.granular_direction == 3 else COLOR.OFF
                )
                self.set_color(
                    15, COLOR.WHITE_MUTED if self.granular_repitch == 1 else COLOR.OFF
                )

            else:
                for i in range(0, 16):
                    self.set_color(i, COLOR.OFF)

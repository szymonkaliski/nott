# adapter for mext
# TODO: add adapter for trellis.py
# FIXME: fix all "happy paths coding" issues


EDGE_RISING = 0
EDGE_FALLING = 1


class BACKEND(object):
    MEXT = 1
    MEXT_SERIAL = 2
    # TRELLIS = 3


class Monome(object):
    callbacks = {}
    leds = [[0 for _ in range(8 * 8)], [0 for _ in range(8 * 8)]]
    dirty_1 = False  # first 8x8 half
    dirty_2 = False  # second 8x8 half

    def __init__(self, backend=BACKEND.MEXT_SERIAL):
        self.backend = backend

        if self.backend == BACKEND.MEXT:
            from mext import Mext

            self.mext = Mext()
            self.mext.set_grid_key_callback(self.handle_grid_key)

        if self.backend == BACKEND.MEXT_SERIAL:
            from mext_serial import MextSerial

            self.mext_serial = MextSerial()
            self.mext_serial.set_grid_key_callback(self.handle_grid_key)

    def handle_grid_key(self, x, y, edge):
        callback_id = "{}x{}".format(x, y)

        if callback_id in self.callbacks:
            self.callbacks[callback_id](x, y, edge)

    def set_led(self, x, y, value):
        if x < 8:
            if self.leds[0][x + y * 8] != value:
                self.dirty_1 = True
                self.leds[0][x + y * 8] = value
        else:
            if self.leds[1][(x - 8) + y * 8] != value:
                self.dirty_2 = True
                self.leds[1][(x - 8) + y * 8] = value

    def set_callback(self, x, y, fn):
        callback_id = "{}x{}".format(x, y)
        self.callbacks[callback_id] = fn

    def update(self):
        if self.backend == BACKEND.MEXT:
            if self.dirty_1:
                self.mext.set_led_map(0, 0, self.leds[0])

            if self.dirty_2:
                self.mext.set_led_map(8, 0, self.leds[1])

        if self.backend == BACKEND.MEXT_SERIAL:
            self.mext_serial.update()

            if self.dirty_1:
                self.mext_serial.set_led_map(0, 0, self.leds[0])

            if self.dirty_2:
                self.mext_serial.set_led_map(8, 0, self.leds[1])

        self.dirty_1 = False
        self.dirty_2 = False

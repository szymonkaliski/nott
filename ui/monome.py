# adapter for mext
# TODO: add adapter for trellis.py
# FIXME: fix all "happy paths coding" issues

from mext import Mext
from threading import Thread
import time

EDGE_RISING = 0
EDGE_FALLING = 1


class Monome(object):
    callbacks = {}
    leds = [[0 for _ in range(8 * 8)], [0 for _ in range(8 * 8)]]

    is_running = False
    thread = None

    def __init__(self):
        self.mext = Mext()
        self.mext.set_grid_key_callback(self.handle_grid_key)

        self.thread = Thread(target=self.run)
        self.thread.setDaemon(True)

    def handle_grid_key(self, x, y, edge):
        callback_id = "{}x{}".format(x, y)

        print(callback_id)

        if self.callbacks[callback_id]:
            self.callbacks[callback_id](x, y, edge)

    def set_led(self, x, y, value):
        if x < 8:
            self.leds[0][x + y * 8] = value
        else:
            self.leds[1][(x - 8) + y * 8] = value

    def set_callback(self, x, y, fn):
        callback_id = "{}x{}".format(x, y)
        self.callbacks[callback_id] = fn

    def update(self):
        self.mext.set_led_map(0, 0, self.leds[0])
        self.mext.set_led_map(8, 0, self.leds[1])

    def start(self):
        self.thread.start()
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):
        while True:
            if self.is_running:
                self.update()

            time.sleep(0.15)

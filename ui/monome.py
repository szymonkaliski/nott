# adapter for mext and trellis (TODO)

from mext import Mext
from threading import Thread
import time

EDGE_RISING = 0
EDGE_FALLING = 1


class Monome(object):
    callbacks = {}
    leds = [[0 for i in range(8)] for i in range(16)]
    prev_leds = [[0 for i in range(8)] for i in range(16)]

    is_running = False
    thread = None

    def __init__(self):
        self.mext = Mext()
        self.mext.set_grid_key_callback(self.handle_grid_key)

        self.thread = Thread(target=self.run)
        self.thread.setDaemon(True)

    def handle_grid_key(self, x, y, edge):
        callback_id = "{}x{}".format(x, y)
        print("handle_grid_key", callback_id, self.callbacks[callback_id])

        if self.callbacks[callback_id]:
            self.callbacks[callback_id](x, y, edge)

    def set_led(self, x, y, value):
        self.leds[x][y] = value

    def set_callback(self, x, y, fn):
        callback_id = "{}x{}".format(x, y)
        self.callbacks[callback_id] = fn

    def update(self):
        for x in range(0, 16):
            for y in range(0, 8):
                if self.leds[x][y] != self.prev_leds[x][y]:
                    self.mext.set_led(x, y, self.leds[x][y])
                    self.prev_leds[x][y] = self.leds[x][y]

    def start(self):
        self.thread.start()
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):
        while True:
            if self.is_running:
                self.update()

            time.sleep(0.01)

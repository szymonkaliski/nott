import busio
import liblo
import signal
import sys
import time

from adafruit_neotrellis.multitrellis import MultiTrellis
from adafruit_neotrellis.neotrellis import NeoTrellis
from board import SCL, SDA
from threading import Thread

from consts import CHUCK_IN_PORT, CHUCK_OUT_PORT, CHUCK_HOST, LOOPS_COUNT
from row import Row
from topbar import Topbar

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

chuck_in = liblo.ServerThread(CHUCK_IN_PORT)
chuck_out = liblo.Address(CHUCK_HOST, CHUCK_OUT_PORT)

rows = list(
    map(lambda i: Row(i, i + 1, trellis, chuck_in, chuck_out), range(LOOPS_COUNT))
)


for row in rows:
    chuck_in.add_method("/status/" + str(row.id), "ffffi", row.on_osc_msg)

chuck_in.start()

topbar = Topbar(rows, trellis)


print("Nótt UI Ready")


class Main(object):
    is_running = True

    def stop(self):
        self.is_running = False

    def run(self):
        while self.is_running:
            topbar.draw()

            for row in rows:
                row.draw()
            trellis.sync()


main = Main()

mainThread = Thread(target=main.run)
mainThread.setDaemon(True)
mainThread.start()


def signal_handler(signal, frame):
    print("Cleanup...")
    main.stop()

    chuck_in.stop()
    topbar.clear()

    for row in rows:
        row.clear()

    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

# main loop

while True:
    time.sleep(100)

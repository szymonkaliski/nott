import busio
import digitalio
import liblo
import signal
import sys
import time

from adafruit_neotrellis.multitrellis import MultiTrellis
from adafruit_neotrellis.neotrellis import NeoTrellis
from board import SCL, SDA, D5
from threading import Thread

from consts import CHUCK_IN_PORT, CHUCK_OUT_PORT, CHUCK_HOST, LOOPS_COUNT
from row import Row
from topbar import Topbar
from patterns import Patterns

# setup trellis
i2c_bus = busio.I2C(SCL, SDA)
trellis = MultiTrellis(
    [
        [
            NeoTrellis(i2c_bus, True, addr=0x31),
            NeoTrellis(i2c_bus, True, addr=0x30),
            NeoTrellis(i2c_bus, True, addr=0x2F),
            NeoTrellis(i2c_bus, True, addr=0x2E),
        ],
        [
            NeoTrellis(i2c_bus, True, addr=0x35),
            NeoTrellis(i2c_bus, True, addr=0x34),
            NeoTrellis(i2c_bus, True, addr=0x33),
            NeoTrellis(i2c_bus, True, addr=0x32),
        ],
    ]
)

# setup chuck osc communication
chuck_in = liblo.ServerThread(CHUCK_IN_PORT)
chuck_out = liblo.Address(CHUCK_HOST, CHUCK_OUT_PORT)

# setup ui
rows = []

patterns = Patterns(
    lambda path, loopId, *values: liblo.send(chuck_out, path, loopId, *values)
)


for i in range(LOOPS_COUNT):
    row = Row(i, i + 1, trellis, chuck_in, patterns.on_msg)
    rows.append(row)
    chuck_in.add_method("/status/" + str(row.id), "iiffffiff", row.on_osc_msg)

topbar = Topbar(rows, patterns, trellis)

# start receiving info from chuck
chuck_in.start()

# interrupt pin - sync only when needed
interrupt = digitalio.DigitalInOut(D5)
interrupt.direction = digitalio.Direction.INPUT

# main thread


class Main(object):
    is_running = True

    def stop(self):
        self.is_running = False

    def run(self):
        print("Nótt UI Ready")

        while self.is_running:
            topbar.draw()

            for row in rows:
                row.draw()

            if interrupt.value is False:
                trellis.sync()


main = Main()

mainThread = Thread(target=main.run)
mainThread.setDaemon(True)
mainThread.start()

# clean exit


def signal_handler(signal, frame):
    print("Nótt UI Cleanup")

    main.stop()
    chuck_in.stop()
    topbar.clear()

    for row in rows:
        row.clear()

    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

# main loop

while True:
    time.sleep(1)

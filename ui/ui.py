import liblo
import signal
import sys
import time

from threading import Thread

from consts import CHUCK_IN_PORT, CHUCK_OUT_PORT, CHUCK_HOST, LOOPS_COUNT
from row import Row
from topbar import Topbar
from patterns import Patterns

from monome import Monome

# setup chuck osc communication
chuck_in = liblo.ServerThread(CHUCK_IN_PORT)
chuck_out = liblo.Address(CHUCK_HOST, CHUCK_OUT_PORT)

# setup monome
monome = Monome()
monome.start()

# setup ui
rows = []

patterns = Patterns(
    lambda path, loopId, *values: liblo.send(chuck_out, path, loopId, *values)
)


for i in range(LOOPS_COUNT):
    row = Row(i, i + 1, monome, chuck_in, patterns.on_msg)
    rows.append(row)
    chuck_in.add_method("/status/" + str(row.id), "siiffffiff", row.on_osc_msg)
    chuck_in.add_method("/status_granular/" + str(row.id), "ffiii", row.on_osc_msg)

topbar = Topbar(rows, patterns, monome)

# start receiving info from chuck
chuck_in.start()

# main


class Main(object):
    is_running = False
    thread = None

    def __init__(self):
        self.thread = Thread(target=self.run)
        self.thread.setDaemon(True)

    def start(self):
        self.thread.start()
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):
        print("Nótt UI Ready")

        while True:
            if self.is_running:
                topbar.draw()

                for row in rows:
                    row.draw()
            else:
                time.sleep(0.01)


main = Main()
main.start()

# clean exit


def signal_handler(signal, frame):
    print("Nótt UI Cleanup")

    main.stop()
    chuck_in.stop()
    patterns.stop()

    topbar.clear()

    for row in rows:
        row.clear()

    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

# main loop

while True:
    time.sleep(1)

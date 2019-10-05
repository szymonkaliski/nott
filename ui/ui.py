import liblo
import signal
import sys
import time

from consts import CHUCK_IN_PORT, CHUCK_OUT_PORT, CHUCK_HOST, LOOPS_COUNT
from row import Row
from topbar import Topbar
from patterns import Patterns

from monome import Monome


# setup chuck osc communication
chuck_in = liblo.ServerThread(CHUCK_IN_PORT, reg_methods=False)
chuck_out = liblo.Address(CHUCK_HOST, CHUCK_OUT_PORT)

# setup monome
monome = Monome()

# setup ui
rows = []


def chuck_send(path, loopId, *values):
    liblo.send(chuck_out, path, loopId, *values)


patterns = Patterns(chuck_send)


for i in range(LOOPS_COUNT):
    row = Row(i, i + 1, monome, patterns.on_msg)
    chuck_in.add_method("/status/" + str(row.id), "siiffffiff", row.on_osc_msg)
    chuck_in.add_method("/status_granular/" + str(row.id), "ffiii", row.on_osc_msg)
    rows.append(row)

topbar = Topbar(rows, patterns, monome)


# clean exit
def signal_handler(signal, frame):
    print("Nótt UI Cleanup")

    chuck_in.stop()
    patterns.stop()

    topbar.clear()

    for row in rows:
        row.clear()

    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

# main loop

chuck_in.start()

print("Nótt UI Ready")

while True:
    monome.update()
    patterns.update()

    topbar.draw()

    for row in rows:
        row.draw()

    time.sleep(0.01)

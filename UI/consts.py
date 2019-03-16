from enum import Enum


CHUCK_HOST = "127.0.0.1"
CHUCK_IN_PORT = 3001
CHUCK_OUT_PORT = 3000

LOOPS_COUNT = 6
RATES = [0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0]


class COLOR(object):
    OFF = (0, 0, 0)
    WHITE_MUTED = (6, 4, 4)
    WHITE = (60, 40, 40)


class MODE(Enum):
    PLAY = 1
    CONTROL_1 = 2
    CONTROL_2 = 3

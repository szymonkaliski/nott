from serial import Serial
from time import time


class MextSerial(object):
    def __init__(self):
        # TODO: set values from config
        self.serial = Serial(
            "/dev/ttyACM0",
            115200,
            # 500000,
            timeout=0,
            # write_timeout=0
        )

    def set_grid_key_callback(self, fn):
        self.grid_key_callback = fn

    def set_led_map(self, x, y, data):
        packed = [0x1A, x, y]

        for i in range(0, len(data), 2):
            packed.append((data[i] & 0xF0) | (data[i + 1] & 0x0F))

        self.serial.write(packed)

    def set_led(self, x, y, value):
        self.serial.write([0x18, x, y, value])

    def update(self):
        if self.serial.in_waiting >= 3:
            r = self.serial.read(3)

            if len(r) != 3:
                print("error reading three bytes from monome", r)
                return

            if r[0] != 32 and r[0] != 33:
                print("unrecognised first byte from monome", r[0])
                return

            edge = 0 if r[0] == 32 else 1
            x = r[1]
            y = r[2]

            if self.grid_key_callback:
                self.grid_key_callback(x, y, edge)

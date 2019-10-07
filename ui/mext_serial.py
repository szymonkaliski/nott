from serial import Serial
import os.path


def first(iterable, condition=lambda x: True):
    return next(x for x in iterable if condition(x))


class MextSerial(object):
    def __init__(self):
        serial_path = first(
            ["/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyACM2"],
            condition=lambda path: os.path.exists(path),
        )

        self.serial = Serial(serial_path, 115200, timeout=0)

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

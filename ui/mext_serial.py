from serial import Serial


class MextSerial(object):
    def __init__(self):
        # TODO: get values from config
        self.serial = Serial(
            "/dev/ttyACM0",
            500000,
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

    def update(self):
        r = self.serial.read(3)

        # only parsing grid buttons

        if len(r) != 3:
            return

        edge = 0 if r[0] == 32 else 1
        x = r[1]
        y = r[2]

        if self.grid_key_callback:
            self.grid_key_callback(x, y, edge)

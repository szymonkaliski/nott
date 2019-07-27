import liblo


class Mext(object):
    device = None

    def __init__(self, device_port=5000):
        self.device_receiver = liblo.ServerThread(device_port)

        self.device_receiver.add_method("/monome/grid/key", "iii", self.on_grid_key)
        self.device_receiver.add_method(
            "/serialosc/device", "ssi", self.on_serialosc_device
        )

        self.device_receiver.start()

        liblo.send(liblo.Address(12002), "/serialosc/list", "127.0.0.1", device_port)

    def set_grid_key_callback(self, fn):
        self.grid_key_callback = fn

    def set_led(self, x, y, value):
        if self.device is None:
            return

        # FIXME: happy path coding...
        liblo.send(self.device, "/monome/grid/led/level/set", x, y, value)

    def on_grid_key(self, path, args):
        x, y, edge = args

        print(x, y, edge)

        if self.grid_key_callback:
            self.grid_key_callback(x, y, edge)

    def on_serialosc_device(self, path, args):
        _, sysId, port = args
        self.device = liblo.Address(port)

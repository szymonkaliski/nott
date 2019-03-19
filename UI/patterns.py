import time


class Patterns(object):
    is_replaying = False
    is_recording = False
    active_idx = 0
    records = {}

    def __init__(self, callback):
        self.callback = callback

    def start_recording(self, idx):
        self.is_recording = True
        self.active_idx = idx
        self.records[self.active_idx] = [{"type": "start", "time": time.time()}]

    def stop_recording(self):
        self.is_recording = False
        self.records[self.active_idx] = [{"type": "stop", "time": time.time()}]

    def clear_recording(self, idx):
        self.is_recording = False
        del self.records[idx]

    def stop_replaying(self):
        self.is_replaying = False

    def start_replaying(self, idx):
        self.active_idx = idx
        self.is_replaying = True

    def on_click(self, idx):
        if idx not in self.records:
            self.start_recording(idx)

            return

        if idx in self.records and self.is_recording:
            self.stop_recording()

            return

        if idx in self.records and not self.is_recording and self.is_replaying:
            self.stop_replaying()

            return

        if idx in self.records and not self.is_recording and not self.is_replaying:
            self.start_replaying(idx)

            return

    def on_msg(self, path, loopId, *values):
        if self.is_recording:
            self.records[self.active_idx].append(
                {
                    "type": "msg",
                    "path": path,
                    "loopId": loopId,
                    "values": values,
                    "time": time.time(),
                }
            )

            print(self.records)

        self.callback(path, loopId, *values)

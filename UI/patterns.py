from threading import Thread
import time


class Patterns(object):
    is_replaying = False
    is_recording = False
    active_idx = 0
    records = {}
    replay_start_time = 0
    replay_last_item_idx = -1

    thread = None

    def __init__(self, callback):
        self.callback = callback

        self.thread = Thread(target=self.run_thread)
        self.thread.setDaemon(True)
        self.thread.start()

    def start_recording(self, idx):
        self.is_recording = True
        self.active_idx = idx
        self.records[self.active_idx] = [
            {"type": "start", "time": time.time(), "dt": 0}
        ]

    def stop_recording(self):
        self.is_recording = False
        self.records[self.active_idx].append(
            {
                "type": "stop",
                "time": time.time(),
                "dt": time.time() - self.records[self.active_idx][0].get("time"),
            }
        )

    def clear_recording(self, idx):
        self.is_recording = False
        del self.records[idx]

    def stop_replaying(self):
        self.is_replaying = False

    def start_replaying(self, idx):
        self.active_idx = idx
        self.is_replaying = True

        self.replay_start_time = time.time()

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

    def stop(self):
        if self.is_recording:
            self.stop_recording()

        if self.is_replaying:
            self.stop_replaying(self.active_idx)

    def on_msg(self, path, loopId, *values):
        if self.is_recording:
            # record the message metadata
            self.records[self.active_idx].append(
                {
                    "type": "msg",
                    "path": path,
                    "loopId": loopId,
                    "values": values,
                    "time": time.time(),
                    "dt": time.time() - self.records[self.active_idx][0].get("time"),
                }
            )

        self.callback(path, loopId, *values)

    def run_thread(self):
        while True:
            if self.is_replaying:
                dt = time.time() - self.replay_start_time

                matching_index = None
                matching_record = None

                for index, record in enumerate(self.records[self.active_idx]):
                    if record.get("dt") >= dt and not matching_index:
                        matching_index = index
                        matching_record = record

                if not matching_index:
                    # if we stepped over the array - start again
                    self.replay_start_time = time.time()
                    self.replay_last_item_idx = -1
                elif (
                    matching_record.get("type") == "msg"
                    and self.replay_last_item_idx != matching_index
                ):
                    # if we have a message that wasn't yet sent, send it out,
                    # and record the index
                    self.replay_last_item_idx = matching_index
                    self.callback(
                        matching_record.get("path"),
                        matching_record.get("loopId"),
                        *matching_record.get("values"),
                    )

            time.sleep(0.01)

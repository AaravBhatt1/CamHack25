import evdev
from evdev.device import InputDevice
import selectors
import threading
import time
import platform


class KeyHook:
    def __init__(self, on_key, on_finish, same_time_delay = 0.00, letter_timeout = 0.8):
        self.buffer = []
        self.same_time_delay = same_time_delay
        self.letter_timeout = letter_timeout
        self.on_finish = on_finish
        self.on_key = on_key
        self.stop_event = threading.Event()
        self.lock = threading.Lock()

    def add_key(self, key):
        timestamp = time.time()
        with self.lock:
            self.buffer.append((key, timestamp))

    def _dispatcher(self):
        while not self.stop_event.is_set():
            time.sleep(0.02)
            with self.lock:
                if not self.buffer:
                    continue
                if time.time() - self.buffer[-1][1] < self.letter_timeout:
                    continue
                seq, tmp, prev_t = [], [], None
                
                for key, t in self.buffer:
                    if prev_t is None or t - prev_t < self.same_time_delay:
                        tmp.append(key)
                    else:
                        seq.append(tmp)
                        tmp = [key]
                    prev_t = t
                if tmp:
                    seq.append(tmp)
                self.buffer.clear()
            if seq:
                self.on_finish(seq)

    def _read_windows(self):
        import keyboard
        while not self.stop_event.is_set():
            ev = keyboard.read_event()
            if ev.event_type == "down":
                name = ev.name.lower()
                if name == "esc":
                    self.stop_event.set()
                    break
                with self.lock:
                    self.buffer.append((name, time.time()))

    def _read_linux(self) -> None:
        keyboards = self._get_keyboards()

        selector = selectors.DefaultSelector()
        for kb in keyboards:
            kb.grab()
            selector.register(kb, selectors.EVENT_READ)
        self._reset_keys(keyboards)

        try:
            while not self.stop_event.is_set():
                for key, _ in selector.select(timeout=0.1):
                    dev = key.fileobj
                    for e in dev.read():
                        if e.type == evdev.ecodes.EV_KEY and e.value == 1:
                            name = evdev.ecodes.KEY[e.code][4:].lower()
                            if name == "esc":
                                self.stop_event.set()
                                break
                            self.on_key(name)
                            with self.lock:
                                self.buffer.append((name, time.time()))
        finally:
            for kb in keyboards:
                try:
                    kb.ungrab()
                except OSError:
                    pass
            self.stop_event.set()


    @staticmethod
    def _reset_keys(kbs: list[InputDevice]) -> None:
        for kb in kbs:
            try:
                for _ in kb.read():
                    pass
            except BlockingIOError:
                pass

    @staticmethod
    def _get_keyboards() -> list[InputDevice]:
        keyboards = []
        for dp in evdev.list_devices():
            d = InputDevice(dp)
            caps = d.capabilities()
            if evdev.ecodes.EV_KEY in caps and \
               evdev.ecodes.EV_REL not in caps and \
               evdev.ecodes.EV_ABS not in caps and \
               "mouse" not in d.name.lower() and \
               "touchpad" not in d.name.lower():
                keyboards.append(d)
        return keyboards


    def start(self):
        sys = platform.system()
        if sys == "Linux":
            target = self._read_linux
        else:
            target = self._read_windows

        reader = threading.Thread(target=target, daemon=True)
        dispatcher = threading.Thread(target=self._dispatcher, daemon=True)

        reader.start()
        dispatcher.start()
        reader.join()
        dispatcher.join()

if __name__ == "__main__":
    def on_finish(groups):
        print(groups)
    def on_key(k):
        print(f"FOUND {k}")
    collector = KeyHook(on_key, on_finish)
    collector.start()

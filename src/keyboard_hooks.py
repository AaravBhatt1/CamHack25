import evdev
from evdev.device import InputDevice
from evdev import UInput
import selectors
import threading
import time
import platform

_stop = threading.Event()
_keyPressBuf = []
_keyPressLock = threading.Lock()


def dispatcher(onFinishDraw, sameTimeDelay=0.0, timeBetweenLetters=0.8):
    global _keyPressBuf, _keyPressLock
    while not _stop.is_set():
        time.sleep(0.01)
        with _keyPressLock:
            if not _keyPressBuf:
                continue
            # check if last key is older than timeBetweenLetters
            if time.time() - _keyPressBuf[-1][1] < timeBetweenLetters:
                continue

            toDispatch = []
            sameTimeAccumulate = []
            for keystr, timestamp in _keyPressBuf:
                if len(sameTimeAccumulate) == 0 or timestamp - sameTimeAccumulate[-1][1] < sameTimeDelay:
                    sameTimeAccumulate.append((keystr, timestamp))
                else:
                    toDispatch.append([k for k, _ in sameTimeAccumulate])
                    sameTimeAccumulate = []
                    toDispatch.append([keystr])
            if sameTimeAccumulate:
                toDispatch.append([k for k, _ in sameTimeAccumulate])

            _keyPressBuf.clear()

        if toDispatch:
            onFinishDraw(toDispatch)


def get_linux_keyboards() -> list[InputDevice]:
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    kbs = []
    for d in devices:
        caps = d.capabilities()
        if evdev.ecodes.EV_KEY in caps and evdev.ecodes.EV_REL not in caps and evdev.ecodes.EV_ABS not in caps:
            kbs.append(d)
    
    return kbs

def reset_keys(kbs: list[InputDevice]):
    with UInput() as ui:
        for d in kbs:
            pressed_keys = d.active_keys()
            for code in pressed_keys:
                ui.write(evdev.ecodes.EV_KEY, code, 0)
        ui.syn()

def linuxKeyReader(onKeyPress):
    global _keyPressBuf, _keyPressLock, _stop
    selector = selectors.DefaultSelector()
    kbs = get_linux_keyboards()

    for d in kbs:
        d.grab()
        selector.register(d, selectors.EVENT_READ)
    reset_keys(kbs)

    try:
        while not _stop.is_set():
            for key, mask in selector.select(timeout=0.1):
                device = key.fileobj
                for e in device.read():
                    event = evdev.categorize(e)
                    if isinstance(event, evdev.events.KeyEvent) and event.keystate == 1 and event.keycode.startswith("KEY_"):
                        _, keystr = event.keycode.split("_")
                        onKeyPress(keystr)
                        if keystr == "ESC":
                            _stop.set()
                            return
                        with _keyPressLock:
                            _keyPressBuf.append((keystr, time.time()))
    finally:
        for d in kbs:
            try:
                d.ungrab()
            except OSError:
                pass
        _stop.set()


def windowsKeyReader(onKeyPress):
    import keyboard
    global _keyPressBuf, _keyPressLock, _stop
    while not _stop.is_set():
        event = keyboard.read_event()
        if event.event_type == "down":
            if event.name == "unknown":
                continue
            if event.name == "esc":
                _stop.set()
                break
            with _keyPressLock:
                _keyPressBuf.append((event.name.upper(), event.time))


def start_listener(onKeyPress, onFinishDraw):
    if platform.system() == "Linux":
        producer = threading.Thread(target=linuxKeyReader, args=(onKeyPress,))
    elif platform.system() == "Windows":
        producer = threading.Thread(target=lambda: windowsKeyReader(onKeyPress))
    else:
        raise Exception("Incompatible platform")

    consumer = threading.Thread(target=lambda: dispatcher(onFinishDraw))

    # start threads
    producer.start()
    consumer.start()

    # block main thread until ESC is pressed
    while not _stop.is_set():
        time.sleep(0.1)

    # wait for threads to clean up
    producer.join()
    consumer.join()
def ofd(x):
    print(x)
def okp(x):
    print(f"RECIEVED {x}")

if __name__ == "__main__":
    start_listener(okp, ofd)

# keystr conventions:
# This is what is used on Linux, currently the windows version does not map to these but it will
# generally, the keystr is an uppercase, one word format of the key (for symbols, it is the not-shifted symbol in words)
"""
letters: uppercase
numbers: as expected
Special keys:
ESC
F1 - F12
DELETE
BACKSPACE
ENTER
RIGHTSHIFT
LEFTSHIFT
GRAVE (`)
MINUS
EQUAL
LEFTBRACE
RIGHTBRACE
SEMICOLON
APOSTROPHE
BACKSLASH
COMMA
DOT
SLASH
TAB
CAPSLOCK
LEFTCTRL
LEFTMETA (left windows)
LEFTALT
SPACE
RIGHTALT
COMPOSE (apps/menu)
Arrow keys: LEFT/DOWN/UP/RIGHT
"""

import evdev
from evdev.device import InputDevice
import keyboard
import selectors
import threading
import time
import platform

_keyPressBuf = []
_keyPressLock= threading.Lock()

_stop = threading.Event()

def dispatcher(onFinishDraw, sameTimeDelay = 0.00, timeBetweenLetters = 0.8):
    global _keyPressBuf
    global _keyPressLock
    while not _stop.is_set():
        time.sleep(0.1)
        if (len(_keyPressBuf) == 0 or time.time() - _keyPressBuf[-1][1] < timeBetweenLetters):
            continue
        toDispatch = []
        with _keyPressLock:
            sameTimeAccumulate = []
            for keystr, timestamp in _keyPressBuf:
                if (len(sameTimeAccumulate) == 0 or timestamp - sameTimeAccumulate[-1][1] < sameTimeDelay):
                    sameTimeAccumulate.append((keystr, timestamp))
                else:
                    toDispatch.append([k for k,_ in sameTimeAccumulate])
                    sameTimeAccumulate = []
                    toDispatch.append([keystr])
            if len(sameTimeAccumulate) > 0:
                toDispatch.append([k for k,_ in sameTimeAccumulate])
        _keyPressBuf = []
        onFinishDraw(toDispatch)


def get_linux_keyboards() -> list[InputDevice]:
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    kbs = []
    for d in devices:
        caps = d.capabilities()
        if evdev.ecodes.EV_KEY in caps and evdev.ecodes.EV_REL not in caps and evdev.ecodes.EV_ABS not in caps:
            kbs.append(d)
    return kbs


def linuxKeyReader(onKeyPress):
    global _keyPressBuf
    global _keyPressLock
    global _stop
    selector = selectors.DefaultSelector()

    kbs = get_linux_keyboards()

    try:
        for i,d in enumerate(kbs):
            d.grab()
            selector.register(d, selectors.EVENT_READ, data=i)
        localStop = False
        while not localStop:
            for key, mask in selector.select():
                device = key.fileobj
                for e in device.read():
                    event = evdev.categorize(e)
                    if isinstance(event, evdev.events.KeyEvent) and event.keystate == 1 and event.keycode.startswith("KEY_"):
                        _,keystr = event.keycode.split("_")
                        onKeyPress(keystr)
                        if (keystr == "ESC"):
                            localStop = True
                            return
                        with _keyPressLock:
                            _keyPressBuf.append((keystr, time.time()))
    finally:
        for d in kbs:
            d.ungrab()
        _stop.set()

def windowsKeyReader(onKeyPress):
    global _keyPressBuf
    global _keyPressLock
    global _stop
    
    while True:
        event = keyboard.read_event()
        if event.event_type == "down":
            if event.name == "unknown":
                continue
            if event.name == "esc":
                break
            with _keyPressLock:
                _keyPressBuf.append((event.name.upper(), event.time))
    _stop.set()
                

def start_listener(onKeyPress, onFinishDraw):
    producer = 0
    if platform.system() == "Linux":
        producer = threading.Thread(target=linuxKeyReader, args=(onKeyPress,), daemon=True)
    elif platform.system() == "Windows":
        producer = threading.Thread(target=lambda : windowsKeyReader(onKeyPress), daemon=True)
    else:
        print("This is only compatible with Windows and Linux")
        raise Exception("Incompatible platform")

    consumer = threading.Thread(target=lambda : dispatcher(onFinishDraw), daemon=True)

    producer.start()
    consumer.start()

    while not _stop.is_set():
        time.sleep(1)

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

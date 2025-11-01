import evdev
import keyboard
import json
import selectors
import threading
import time
import platform

_keyPressBuf = []
_keyPressLock= threading.Lock()

_stop = False

def dispatcher(onFinishDraw, sameTimeDelay = 0.04, timeBetweenLetters = 0.8):
    global _keyPressBuf
    global _keyPressLock
    while not _stop:
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



def linuxKeyReader(onKeyPress):
    global _keyPressBuf
    global _keyPressLock
    global _stop
    selector = selectors.DefaultSelector()

    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    forwarderDevices = [evdev.UInput.from_device(dev, name=f"{dev.name}-forwarded") for dev in devices]
    try:
        for i,d in enumerate(devices):
            d.grab()
            selector.register(d, selectors.EVENT_READ, data=i)
        localStop = False
        while not localStop:
            for key, mask in selector.select():
                device = key.fileobj
                index = int(key.data)
                for e in device.read():
                    event = evdev.categorize(e)
                    # print(event, type(event), "\n\n")
                    if isinstance(event, evdev.events.KeyEvent) and event.keystate == 1 and event.keycode.startswith("KEY_"):
                        _,keystr = event.keycode.split("_")
                        timestamp = event.event.timestamp()
                        onKeyPress(keystr)
                        if (keystr == "ESC"):
                            localStop = False
                            return
                        with _keyPressLock:
                            _keyPressBuf.append((keystr, timestamp))
                    else:
                        # Forward the event
                        forwarderDevices[index].write_event(event)
                        forwarderDevices[index].syn()
    finally:
        for d in devices:
            d.ungrab()
        for ui in forwarderDevices:
            ui.close()
        _stop = True

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
                _keyPressBuf.append((event.name.upper, event.time))
    _stop = True
                

def main(onKeyPress, onFinishDraw):
    producer = 0
    if platform.system() == "Linux":
        producer = threading.Thread(target=lambda : linuxKeyReader(onKeyPress), daemon=True)
    elif platform.system() == "Windows":
        producer = threading.Thread(target=lambda : windowsKeyReader(onKeyPress), daemon=True)
    else:
        print("This is only compatible with Windows and Linux")
        raise Exception("Incompatible platform")

    consumer = threading.Thread(target=lambda : dispatcher(ofd), daemon=True)

    producer.start()
    consumer.start()

    while not _stop:
        time.sleep(1)

def ofd(x):
    print(x)
def okp(x):
    print(f"RECIEVED {x}")

if __name__ == "__main__":
    main(okp, ofd)

# keystr conventions:
# This is what is used on Linux, currently the windows version does not map to these but it will
# generally, the keystr is an uppercase, one word format of the key (for symbols, it is the not-shifted symbol in words)
"""
letters: uppercase
numbers: as expected
Special keys:
ESC done
F1 - F12 done
DELETE done
BACKSPACE done
ENTER done
RIGHTSHIFT done
LEFTSHIFT done 
GRAVE (`) done
MINUS done 
EQUAL done
LEFTBRACE done
RIGHTBRACE done
SEMICOLON  done
APOSTROPHE done
BACKSLASH done
COMMA done 
DOT done
SLASH done 
TAB done
CAPSLOCK done
LEFTCTRL done
LEFTMETA (left windows) done
LEFTALT done
SPACE done
RIGHTALT done 
COMPOSE (apps/menu)
Arrow keys: LEFT/DOWN/UP/RIGHT done
"""

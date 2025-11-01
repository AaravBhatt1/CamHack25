import evdev
import json
import selectors
import threading
import time


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



def keyReader():
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
def main(onFinishDraw):
    producer = threading.Thread(target=keyReader, daemon=True)
    consumer = threading.Thread(target=lambda : dispatcher(ofd), daemon=True)

    producer.start()
    consumer.start()

    while not _stop:
        time.sleep(1)

def ofd(x):
    print(x)

if __name__ == "__main__":
    main(ofd)


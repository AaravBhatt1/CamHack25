import keyboard
import json

def onKeyPress(char):
    print(char)




def main(onCharPress):
    while True:
        event = keyboard.read_event()
        if event.event_type == "down":
            if event.name == "esc":
                break
            if event.name != "unknown":
                onCharPress(event.name)

        #print(json.dumps(json.loads(event.to_json()), indent=4))

if __name__ == "__main__":
    main(onKeyPress)


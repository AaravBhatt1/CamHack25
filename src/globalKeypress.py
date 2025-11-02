from pynput.keyboard import Key, Controller
import time

keyboard = Controller()

def type_string(text):
    for char in text:
        keyboard.press(char)
        keyboard.release(char)
        time.sleep(0.01) # Small delay helps prevent missed inputs

# Output "Hello World!" as global keypresses
# type_string("Hello World!")
print("Starting in 4 seconds...")
time.sleep(4)  # Give you time to switch to the target window

try:
    print("Now attempting to press keys...")
    # Try a special key first
    print("Pressing space bar...")
    keyboard.press(Key.space)
    keyboard.release(Key.space)
    time.sleep(1)
    
    print("Pressing letter 'a'...")
    for i in range(5):
        print(f"Press {i+1}")
        keyboard.press('a')
        keyboard.release('a')
        time.sleep(0.5)  # Longer delay to make it more noticeable
        
    print("Done pressing keys.")
except Exception as e:
    print(f"An error occurred: {e}")
import tkinter as tk
import time
from queue import Empty
from multiprocessing.managers import BaseManager
import sys

# Coordinate map for keys
# Key: (X_position, Y_position).
KEY_MAP = {
    # Number row
    'GRAVE': (50, 50), '1': (100, 50), '2': (150, 50), '3': (200, 50), '4': (250, 50),
    '5': (300, 50), '6': (350, 50), '7': (400, 50), '8': (450, 50), '9': (500, 50),
    '0': (550, 50), 'MINUS': (600, 50), 'EQUAL': (650, 50),
    'BACKSPACE': (725, 50),
    
    # Top letter row
    'TAB': (75, 100),
    'Q': (125, 100), 'W': (175, 100), 'E': (225, 100), 'R': (275, 100),
    'T': (325, 100), 'Y': (375, 100), 'U': (425, 100), 'I': (475, 100),
    'O': (525, 100), 'P': (575, 100), 'LEFTBRACE': (625, 100), 'RIGHTBRACE': (675, 100),
    
    # Home row
    'CAPSLOCK': (90, 150),
    'A': (150, 150), 'S': (200, 150), 'D': (250, 150), 'F': (300, 150),
    'G': (350, 150), 'H': (400, 150), 'J': (450, 150), 'K': (500, 150),
    'L': (550, 150), 'SEMICOLON': (600, 150), 'APOSTROPHE': (650, 150),
    'ENTER': (725, 150),
    
    # Bottom row
    'LEFTSHIFT': (100, 200), 'BACKSLASH': (135, 200),
    'Z': (175, 200), 'X': (225, 200), 'C': (275, 200), 'V': (325, 200),
    'B': (375, 200), 'N': (425, 200), 'M': (475, 200), 'COMMA': (525, 200),
    'DOT': (575, 200), 'SLASH': (625, 200),
    'RIGHTSHIFT': (700, 200),

    # Bottom row - modifiers
    'LEFTCTRL': (75, 250),
    'LEFTMETA': (125, 250),
    'LEFTALT': (175, 250),
    'SPACE': (400, 250),  # Centered, wide key
    'RIGHTALT': (625, 250),
    'COMPOSE': (725, 250),  # Menu/Apps key
    
    # Arrow keys
    'LEFT': (625, 300),
    'DOWN': (675, 300),
    'RIGHT': (725, 300),
    'UP': (675, 250),
    
    # Additional keys
    'ESC': (50, 25),
    'DELETE': (725, 75),
    'HOME': (625, 75),
    'END': (675, 75),
    'PAGEUP': (625, 25),
    'PAGEDOWN': (675, 25)
}

flip = False

# --- Global State ---
key_history = []
MAX_HISTORY = 200 # Only display the last 25 keypresses

class QueueManager(BaseManager): pass

def on_press(key):
    if key in KEY_MAP:
        # Get position from map
        x, y = KEY_MAP[key]
        if flip:
            pos = (y, x)  
        else:
            pos = (x, y) 
        
        # Update key history
        key_history.append((key, pos, 0))
        if len(key_history) > MAX_HISTORY:
            key_history.pop(0)
            
        # Request a screen update
        root.after(10, update_display)

def update_display():
    """Clears the canvas and draws the current key history."""
    canvas.delete("all") # Clear previous drawing
    
    # title_text = "LAST 10 KEYPRESSES (QWERTY LAYOUT)"
    # canvas.create_text(300, 20, text=title_text, fill='white', font=('Arial', 14))

    # Draw a dim background circle for every key
    # for key_char, (x, y) in KEY_MAP.items():    
    #     canvas.create_oval(x-15, y-15, x+15, y+15, outline='#333333')
    
    # Draw keypress history in reverse order (most recent is brightest/largest)
    for key_char, (x, y), frame in key_history:
        # Calculate size and brightness based on recency
        alpha =  1 - (((frame + 1) * 0.5) / MAX_HISTORY) # Closer to 1 for recent keys
        size = 20
        color_hex = f'#{int(255 * alpha):02x}{int(100 * alpha):02x}{0:02x}' # Fade from Red

        # Draw the keypress circle
        canvas.create_oval(x-size, y-size, x+size, y+size, fill=color_hex, outline=color_hex)
        
        # Draw the key character label
        label = key_char.char if hasattr(key_char, 'char') else str(key_char).split('.')[-1].upper()
        canvas.create_text(x, y, text=label, fill='white', font=('Arial', 10, 'bold'))

    root.update_idletasks() # Force redraw

def clearDisplay():
    global key_history
    key_history = []
    root.after(10, update_display)

# Queue polling
def check_queue(root, q, delay = 10):
    #print("CHECKING QQQ")
    #q = m.get_queue()
    if running:
        global key_history
        key_history = [(key, pos, i+1) for (key, pos, i) in key_history if i < MAX_HISTORY]

        update_display()
        try:
            key = str(q.get_nowait()).upper()
            print("K", key)
            if key == "STOP":
                clearDisplay()
            elif key != 'ESC':  # Check if key is not ESC
                on_press(key)
        except Empty:
            print("EEEEMPT")
        finally:

            root.after(delay, check_queue, root, q)  # Schedule next check

# To be called when the Tkinter window closes
def on_closing():
    global running
    running = False
    root.destroy()

if __name__ == "__main__":
    if len(sys.argv > 1):
        arg = sys.argv[1]
        flip = arg == "flip"

    # Global flag to control the queue polling loop
    running = True  
    
    # Tkinter Setup
    root = tk.Tk()
    root.title("Real-Time Keyboard Visualizer")
    w = 1000
    h = 500
    if flip: 
        w,h = h,w
    canvas = tk.Canvas(root, width=w, height=h, bg='black')
    canvas.pack()
    
    # Set up window close handler
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Server setup 
    QueueManager.register('get_queue')

    # The only thing being sent through this queue is characters so authkey=b'abc' is fine
    m = QueueManager(address=('localhost', 50000), authkey=b'abc')
    m.connect()
    q = m.get_queue()
    # Start queue checking
    check_queue(root, q)
    
    # Start tk window loop
    root.mainloop()

    print("Window closed, shutting down...")
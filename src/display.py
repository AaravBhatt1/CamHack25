import tkinter as tk
import time
from Queue import Empty
from multiprocessing.managers import BaseManager

# --- Configuration ---
# Define a comprehensive coordinate map for keys based on a standard QWERTY layout.
# Key: (X_position, Y_position) - scaled for a typical canvas size.
KEY_MAP = {
    # Previous keyboard mapping
    # # Number row
    # '`': (50, 50), '1': (100, 50), '2': (150, 50), '3': (200, 50), '4': (250, 50),
    # '5': (300, 50), '6': (350, 50), '7': (400, 50), '8': (450, 50), '9': (500, 50),
    # '0': (550, 50), '-': (600, 50), '=': (650, 50),
    # keyboard.Key.backspace: (725, 50),
    
    # # Top letter row
    # keyboard.Key.tab: (75, 100),
    # 'q': (125, 100), 'w': (175, 100), 'e': (225, 100), 'r': (275, 100),
    # 't': (325, 100), 'y': (375, 100), 'u': (425, 100), 'i': (475, 100),
    # 'o': (525, 100), 'p': (575, 100), '[': (625, 100), ']': (675, 100),
    
    # # Home row
    # keyboard.Key.caps_lock: (90, 150),
    # 'a': (150, 150), 's': (200, 150), 'd': (250, 150), 'f': (300, 150),
    # 'g': (350, 150), 'h': (400, 150), 'j': (450, 150), 'k': (500, 150),
    # 'l': (550, 150), ';': (600, 150), "'": (650, 150),
    # keyboard.Key.enter: (725, 150),
    
    # # Bottom row
    # keyboard.Key.shift: (100, 200), '\\': (135, 200),
    # 'z': (175, 200), 'x': (225, 200), 'c': (275, 200), 'v': (325, 200),
    # 'b': (375, 200), 'n': (425, 200), 'm': (475, 200), ',': (525, 200),
    # '.': (575, 200), '/': (625, 200),
    # keyboard.Key.shift_r: (700, 200),

    # New keyboard mapping using keyboard_hooks.py conventions
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

# --- Global State ---
key_history = []
MAX_HISTORY = 10 # Only display the last 10 keypresses

class QueueManager(BaseManager): pass

def on_press(key):
   
    if key in KEY_MAP or key in ['D']:
        # Get position from map
        pos = KEY_MAP[key]        
        
        # Update key history
        key_history.append((key, pos))
        if len(key_history) > MAX_HISTORY:
            key_history.pop(0)
            
        # Request a screen update
        root.after(10, update_display)

def update_display():
    """Clears the canvas and draws the current key history."""
    canvas.delete("all") # Clear previous drawing
    
    title_text = "LAST 10 KEYPRESSES (QWERTY LAYOUT)"
    canvas.create_text(300, 20, text=title_text, fill='white', font=('Arial', 14))

    # Draw a representation of all tracked keys for context

    # for key_char, (x, y) in KEY_MAP.items():
    #     # Draw a dim background circle for all available keys
    #     canvas.create_oval(x-15, y-15, x+15, y+15, outline='#333333')
    
    # Draw keypress history in reverse order (most recent is brightest/largest)
    for i, (key_char, (x, y)) in enumerate(reversed(key_history)):
        # Calculate size and brightness based on recency
        alpha = (i + 1) / MAX_HISTORY # Closer to 1 for recent keys
        size = 10 + (MAX_HISTORY - i) * 1.5 # Larger for recent keys
        color_hex = f'#{int(255 * alpha):02x}{int(100 * alpha):02x}{0:02x}' # Fade from Red

        # Draw the keypress circle
        canvas.create_oval(x-size, y-size, x+size, y+size, fill=color_hex, outline=color_hex)
        
        # Draw the key character label
        label = key_char.char if hasattr(key_char, 'char') else str(key_char).split('.')[-1].upper()
        canvas.create_text(x, y, text=label, fill='white', font=('Arial', 10, 'bold'))

    root.update_idletasks() # Force redraw

# Queue polling
def check_queue(root, q, delay = 50):
    if running:
        try:
            key = str(q.get_nowait()).upper()[1:-1]
            if key != 'ESC':  # Check if key is not ESC
                on_press(key)
        except Empty:
            pass
        finally:
            root.after(delay, check_queue, root, q)  # Schedule next check

# To be called when the Tkinter window closes
def on_closing():
    global running
    running = False
    root.destroy()

if __name__ == "__main__":
    # Global flag to control the queue polling loop
    running = True  
    
    # Tkinter Setup
    root = tk.Tk()
    root.title("Real-Time Keyboard Visualizer")
    canvas = tk.Canvas(root, width=1000, height=400, bg='black')
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

# Stop the listener thread when the Tkinter window is closed
# listener.stop()
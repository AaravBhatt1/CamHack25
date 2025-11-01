import tkinter as tk
from pynput import keyboard

# --- Configuration ---
# Define a comprehensive coordinate map for keys based on a standard QWERTY layout.
# Key: (X_position, Y_position) - scaled for a typical canvas size.
KEY_MAP = {
    # Number row
    '`': (50, 50), '1': (100, 50), '2': (150, 50), '3': (200, 50), '4': (250, 50),
    '5': (300, 50), '6': (350, 50), '7': (400, 50), '8': (450, 50), '9': (500, 50),
    '0': (550, 50), '-': (600, 50), '=': (650, 50),
    keyboard.Key.backspace: (725, 50),
    
    # Top letter row
    keyboard.Key.tab: (75, 100),
    'q': (125, 100), 'w': (175, 100), 'e': (225, 100), 'r': (275, 100),
    't': (325, 100), 'y': (375, 100), 'u': (425, 100), 'i': (475, 100),
    'o': (525, 100), 'p': (575, 100), '[': (625, 100), ']': (675, 100),
    
    # Home row
    keyboard.Key.caps_lock: (90, 150),
    'a': (150, 150), 's': (200, 150), 'd': (250, 150), 'f': (300, 150),
    'g': (350, 150), 'h': (400, 150), 'j': (450, 150), 'k': (500, 150),
    'l': (550, 150), ';': (600, 150), "'": (650, 150),
    keyboard.Key.enter: (725, 150),
    
    # Bottom row
    keyboard.Key.shift: (100, 200), '\\': (135, 200),
    'z': (175, 200), 'x': (225, 200), 'c': (275, 200), 'v': (325, 200),
    'b': (375, 200), 'n': (425, 200), 'm': (475, 200), ',': (525, 200),
    '.': (575, 200), '/': (625, 200),
    keyboard.Key.shift_r: (700, 200),
    
    # Bottom row - modifiers and space
    keyboard.Key.ctrl_l: (75, 250),
    keyboard.Key.cmd: (125, 250),
    keyboard.Key.alt_l: (175, 250),
    keyboard.Key.space: (400, 250),  # Centered, wide key
    keyboard.Key.alt_gr: (625, 250),
    keyboard.Key.menu: (675, 250),
    keyboard.Key.ctrl_r: (725, 250),
    
    # Arrow keys
    keyboard.Key.left: (625, 300),
    keyboard.Key.down: (675, 300),
    keyboard.Key.right: (725, 300),
    keyboard.Key.up: (675, 250),
    
    # Additional keys
    keyboard.Key.esc: (50, 25),
    keyboard.Key.delete: (725, 75),
    keyboard.Key.home: (625, 75),
    keyboard.Key.end: (675, 75),
    keyboard.Key.page_up: (625, 25),
    keyboard.Key.page_down: (675, 25)
}

# --- Global State ---
key_history = []
MAX_HISTORY = 10 # Only display the last 10 keypresses

# --- Tkinter Setup ---
root = tk.Tk()
root.title("Real-Time Keyboard Visualizer")
canvas = tk.Canvas(root, width=1000, height=400, bg='black')
canvas.pack()

def on_press(key):
    try:
        # Get the character or key name
        key_char = key.char if hasattr(key, 'char') else key 
    except AttributeError:
        # For special keys like Shift, Ctrl, etc., just use the key object
        key_char = key

    if key_char in KEY_MAP:
        # 1. Get position from map
        pos = KEY_MAP[key_char]
        
        # 2. Update key history
        key_history.append((key_char, pos))
        if len(key_history) > MAX_HISTORY:
            key_history.pop(0)
            
        # 3. Request a screen update
        # Tkinter will call the update_display function shortly
        root.after(10, update_display)

    # Note: Returning False stops the listener. We want it to run continuously.
    # print(f'{key_char} pressed')


def update_display():
    """Clears the canvas and draws the current key history."""
    canvas.delete("all") # Clear previous drawing
    
    title_text = "LAST 10 KEYPRESSES (QWERTY LAYOUT)"
    canvas.create_text(300, 20, text=title_text, fill='white', font=('Arial', 14))

    # # Draw a representation of all tracked keys for context
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

    # Create and start the listener thread
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Start the Tkinter main loop
root.mainloop()

# Stop the listener thread when the Tkinter window is closed
listener.stop()
from typing import Tuple
from typing import Protocol, TypeVar

Number = TypeVar('Number', int, float)



class CharMapper:
    def __init__(self, layout="English", rotate=True):
        # Currently Does Not Do Anything
        self.layout = layout
        self.rotate = rotate

    def charMap(self, char:str) -> Tuple[Number, Number] | None:
        if self.layout == "English":
            # Define keyboard layout coordinates (x, y) for British English MacBook layout
            keyboard_map = {

                #F keys
                "ESC":(0, 0),
                "F1": (1, 0),
                "F2": (2, 0),
                "F3": (3, 0),
                "F4": (4, 0),
                "F5": (5, 0),
                "F6": (6, 0),
                "F7": (7, 0),
                "F8": (8, 0),
                "F9": (9, 0),
                "F10": (10, 0),
                "F11": (11, 0),
                "F12": (12, 0),

                # Number row
                "GRAVE": (0, -1),
                "1": (1, -1),
                "2": (2, -1),
                "3": (3, -1),
                "4": (4, -1),
                "5": (5, -1),
                "6": (6, -1),
                "7": (7, -1),
                "8": (8, -1),
                "9": (9, -1),
                "0": (10, -1),
                "MINUS": (11, -1),
                "EQUAL": (12, -1),
                "BACKSPACE": (13, -1),

                # Top row (QWERTY)
                "TAB": (0, -2),
                "Q": (1.5, -2),
                "W": (2.5, -2),
                "E": (3.5, -2),
                "R": (4.5, -2),
                "T": (5.5, -2),
                "Y": (6.5, -2),
                "U": (7.5, -2),
                "I": (8.5, -2),
                "O": (9.5, -2),
                "P": (10.5, -2),
                "LEFTBRACE": (10.5, -2),
                "RIGHTBRACE": (11.5, -2),

                # Middle row (ASDF)
                "CAPS":(1, -3),
                "A": (1.75, -3),
                "S": (2.75, -3),
                "D": (3.75, -3),
                "F": (4.75, -3),
                "G": (5.75, -3),
                "H": (6.75, -3),
                "J": (7.75, -3),
                "K": (8.75, -3),
                "L": (9.75, -3),
                "SEMICOLON": (9.75, -3),
                "APOSTROPHE": (10.75, -3),
                "BACKSLASH": (11.75, -3),
                "ENTER":(12.75, -3),
                # Bottom row (ZXCV)
                "LEFTSHIFT": (0.25, -4),
                "Z": (1.25, -4),
                "X": (2.25, -4),
                "C": (3.25, -4),
                "V": (4.25, -4),
                "B": (5.25, -4),
                "N": (6.25, -4),
                "M": (7.25, -4),
                "COMMA": (8.25, -4),
                "DOT": (9.25, -4),
                "SLASH": (10.25, -4),
                "RIGHTSHIFT": (11.25, -4),

                # Space ROW
                "LEFTCTRL": (0, -5),
                "LEFTMETA": (2, -5),
                "LEFTALT" : (3.5, -5),
                "SPACE": (5, -5),
                "RIGHTALT": (9.25, -5),

                "LEFT": (11.25, -5),
                "DOWN": (12, -5),
                "RIGHT": (12.75, -5),
                "UP": (12, -5),
            }

            # Convert to lowercase for case-insensitive lookup
            char = char.lower()

            # Get coordinates if character exists in map
            coords = keyboard_map[char]

            # Apply rotation if rotate is True (90 degrees clockwise)
            if self.rotate:
                x, y = coords
                # 90 degree clockwise rotation with y-axis going down (negative)
                # Original: x range 0-12, y range 0 to -4
                # 90° clockwise: (x, y) -> (-y, x)
                rotated_coords = (-y, x)
                return rotated_coords
            else:
                return coords


    def averagePoints(self, chars:list[list[str]]) -> list[Tuple[Number, Number]]:
        o = []
        for i in chars:
            nl:list[Tuple[Number, Number]] = [x for x in map(self.charMap, i) if x is not None]
            if nl == []:
                continue
            o.append((sum(map(lambda x:x[0], nl)) / len(nl), sum(map(lambda x:x[1], nl)) / len(nl)))
        return o

    def movePoints(self, points:list[tuple[Number, Number]]):
        translateX = min(map(lambda x:x[0], points))
        return list(map(lambda x: (x[0] - translateX, x[1]), points))



# TEST
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # Create a CharMapper instance
    mapper = CharMapper()

    # Get input from user
    text = input("Type some keys: ")

    # Get coordinates for each character
    x_coords = []
    y_coords = []

    for char in text:
        try:
            coords = mapper.charMap(char)
            if coords:
                x_coords.append(coords[0])
                y_coords.append(coords[1])
        except KeyError:
            print(f"Character '{char}' not found in keyboard map")

    # Create the plot
    if x_coords and y_coords:
        plt.figure(figsize=(12, 6))
        plt.scatter(x_coords, y_coords, s=100, alpha=0.7)

        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.title("Keyboard Key Positions")
        plt.grid(True, alpha=0.3)
        plt.show()
    else:
        print("No valid characters to plot")

from typing import Tuple
from typing import Protocol, TypeVar

Number = TypeVar("Number", int, float)


class CharMapper:
    def __init__(self, layout="English", rotate=False):
        # Currently Does Not Do Anything
        self.layout = layout
        self.rotate = rotate

    def charMap(self, char: str) -> Tuple[Number, Number] | None:
        if self.layout == "English":
            # Define keyboard layout coordinates (x, y) for British English
            keyboard_map = {
                # Number row
                "grave": (0, 0),
                "1": (1, 0),
                "2": (2, 0),
                "3": (3, 0),
                "4": (4, 0),
                "5": (5, 0),
                "6": (6, 0),
                "7": (7, 0),
                "8": (8, 0),
                "9": (9, 0),
                "0": (10, 0),
                "minus": (11, 0),
                "equal": (12, 0),
                # Top row (QWERTY)
                "q": (0.5, 1),
                "w": (1.5, 1),
                "e": (2.5, 1),
                "r": (3.5, 1),
                "t": (4.5, 1),
                "y": (5.5, 1),
                "u": (6.5, 1),
                "i": (7.5, 1),
                "o": (8.5, 1),
                "p": (9.5, 1),
                "leftbrace": (10.5, 1),
                "rightbrace": (11.5, 1),
                # Middle row (ASDF)
                "a": (0.75, 2),
                "s": (1.75, 2),
                "d": (2.75, 2),
                "f": (3.75, 2),
                "g": (4.75, 2),
                "h": (5.75, 2),
                "j": (6.75, 2),
                "k": (7.75, 2),
                "l": (8.75, 2),
                "semicolon": (9.75, 2),
                "apostrophe": (10.75, 2),
                "102nd": (11.75, 2),
                # Bottom row (ZXCV)
                "z": (1.25, 3),
                "x": (2.25, 3),
                "c": (3.25, 3),
                "v": (4.25, 3),
                "b": (5.25, 3),
                "n": (6.25, 3),
                "m": (7.25, 3),
                "comma": (8.25, 3),
                "dot": (9.25, 3),
                "slash": (10.25, 3),
                # Space bar
                "space": (5, 4),
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

    def averagePoints(self, chars: list[list[str]]) -> list[Tuple[Number, Number]]:
        o = []
        for i in chars:
            nl: list[Tuple[Number, Number]] = [
                x for x in map(self.charMap, i) if x is not None
            ]
            if nl == []:
                continue
            o.append(
                (
                    sum(map(lambda x: x[0], nl)) / len(nl),
                    sum(map(lambda x: x[1], nl)) / len(nl),
                )
            )
        return o

    def movePoints(self, points: list[tuple[Number, Number]]):
        translateX = min(map(lambda x: x[0], points))
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

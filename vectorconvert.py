import numpy as np
from scipy.interpolate import splprep, splev
import matplotlib.pyplot as plt

pixels = [
    (4, 2, 0),
    (5, 1, 1),
    (6, 1, 2),
    (6, 2, 3),
    (5, 3, 4),
    (4, 3, 5),
    (4, 2, 6),
    (6, 2, 7),
    (6, 3, 8),
    (7, 3, 9)
]

def is_adjacent(a, b):
    return abs(a[0]-b[0]) <= 1 and abs(a[1]-b[1]) <= 1


def get_strokes(data):
    sorted_data = sorted(data, key = lambda p: p[2])
    strokes = []
    current = [data[0]]
    for i in range(1, len(sorted_data)):
        if not is_adjacent(sorted_data[i], sorted_data[i-1]):
            strokes.append(current)
            current = [sorted_data[i]]
        else:
            current.append(sorted_data[i])
    strokes.append(current)
    return strokes

def get_curve(x, y):
    tck, u = splprep([x, y], s=0, k=min(3, len(x)-1))
    u_fine = np.linspace(0, 1, 200)
    return splev(u_fine, tck)

def get_curve2(x, y, points=200):
    x = np.array(x)
    y = np.array(y)

    if len(x) < 4:
        return x, y
    t = np.linspace(0, 1, len(x))
    t_fine = np.linspace(0, 1, points)
    

plt.figure(figsize=(10,10))

for stroke in get_strokes(pixels):
    x = [p[0] for p in stroke]
    y = [p[1] for p in stroke]
    x_fine, y_fine = get_curve(x, y)
    plt.plot(x_fine, y_fine, '-')
    plt.scatter(x, y, color='red')

plt.gca().invert_yaxis()
plt.show()

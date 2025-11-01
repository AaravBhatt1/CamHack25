import numpy as np
from scipy.interpolate import splprep, splev
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt

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
    print(strokes)
    return strokes

def get_curve(x, y, noise=0.01):
    if (len(x) < 3):
        return x, y
    tck, u = splprep([x, y], s=0, k=min(3, len(x)-1))
    u_fine = np.linspace(0, 1, 200)
    x_smooth, y_smooth = splev(u_fine, tck)
    x_smooth += np.random.normal(0, noise, size=x_smooth.shape)
    y_smooth += np.random.normal(0, noise, size=y_smooth.shape)
    return x_smooth, y_smooth


def get_bins(x, y, noise=0.30):
    x = np.array(x)
    y = np.array(y)
    x -= x.mean()
    y -= y.mean()
    scale = max(x.max() - x.min(), y.max() - y.min(), 1e-5)
    x /= scale
    y /= scale
    x = (x + 0.5) * 27
    y = (y + 0.5) * 27

    grid, _, _ = np.histogram2d(y, x, bins=28, range=[[0, 27], [0, 27]])
    grid = gaussian_filter(grid, sigma=noise)

    if grid.max() > 0:
        grid /= grid.max()
    grid = grid ** 0.025
    bw_grid = grid
    return bw_grid

def get_image_for_ocr(data):
    x = np.array([])
    y = np.array([])

    for stroke in get_strokes(data):
        x_stroke = [p[0] for p in stroke]
        y_stroke = [p[1] for p in stroke]
        x_fine, y_fine = get_curve(x_stroke, y_stroke)
        x = np.concatenate([x, x_fine])
        y = np.concatenate([y, y_fine])
    return get_bins(x, y)

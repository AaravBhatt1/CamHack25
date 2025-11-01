import numpy as np
from scipy.interpolate import splprep, splev
from scipy.ndimage import gaussian_filter

def _is_adjacent(a: tuple[float, float], b: tuple[float, float]) -> bool:
    return abs(a[0]-b[0]) <= 1 and abs(a[1]-b[1]) <= 1

def _get_strokes(data: list[tuple[float, float]]) -> list[list[tuple[float, float]]]:
    if not data:
        return []
    strokes = []
    current = [data[0]]
    for i in range(1, len(data)):
        if not _is_adjacent(data[i], data[i-1]):
            strokes.append(current)
            current = [data[i]]
        else:
            current.append(data[i])
    strokes.append(current)
    return strokes

def _get_curve(x: list[float], y: list[float], noise=0.01) -> tuple[np.ndarray, np.ndarray]:
    if (len(x) < 3):
        return np.array(x), np.array(y)
    tck, _ = splprep([x, y], s=0, k=min(3, len(x)-1))
    u_fine = np.linspace(0, 1, 200)

    x_smooth, y_smooth = splev(u_fine, tck)
    x_smooth += np.random.normal(0, noise, size=x_smooth.shape)
    y_smooth += np.random.normal(0, noise, size=y_smooth.shape)
    return x_smooth, y_smooth


def _get_bins(x: np.ndarray, y: np.ndarray, noise=0.30) -> np.ndarray:
    x -= x.mean()
    y -= y.mean()
    scale = max(x.max() - x.min(), y.max() - y.min(), 1e-5)
    x /= scale
    y /= scale
    x = (x + 0.5) * 27
    y = (y + 0.5) * 27

    grid, *_ = np.histogram2d(y, x, bins=28, range=[[0, 27], [0, 27]])
    grid = gaussian_filter(grid, sigma=noise)

    if grid.max() > 0:
        grid /= grid.max()
    grid = grid ** 0.025
    bw_grid = grid
    return bw_grid

def get_image_for_ocr(data: list[tuple[float, float]]) -> np.ndarray:
    x = np.array([])
    y = np.array([])

    for stroke in _get_strokes(data):
        x_stroke = [p[0] for p in stroke]
        y_stroke = [p[1] for p in stroke]
        x_fine, y_fine = _get_curve(x_stroke, y_stroke)
        x = np.concatenate([x, x_fine])
        y = np.concatenate([y, y_fine])
    return _get_bins(x, y)

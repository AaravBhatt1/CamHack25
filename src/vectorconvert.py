import numpy as np
import cv2

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
            if _is_adjacent(strokes[-1][0], strokes[-1][-1]):
                strokes[-1].append(strokes[-1][0])
            current = [data[i]]
        else:
            current.append(data[i])

    strokes.append(current)
    if _is_adjacent(strokes[-1][0], strokes[-1][-1]):
        strokes[-1].append(strokes[-1][0])
    return strokes

def _normalise_points(points) -> list[tuple[float, float]]:
    x = np.array([p[0] for p in points], dtype=np.float32)
    y = np.array([p[1] for p in points], dtype=np.float32)

    x -= x.mean()
    y -= y.mean()

    scale = max(x.max() - x.min(), y.max() - y.min(), 1e-5)
    x /= scale
    y /= scale
    x *= 20
    y *= 20

    x += 14
    y += 14
    return list(zip(x, y))

def _normalise_strokes(strokes, norm_points):
    offset = 0
    norm_strokes = []
    for s in strokes:
        n = len(s)
        norm_strokes.append(norm_points[offset:offset+n])
        offset += n
    return norm_strokes

def get_image_for_ocr(data: list[tuple[float, float]], sideways_keyboard: bool=False) -> np.ndarray:
    img = np.zeros((28, 28), dtype=np.float32)

    strokes = _get_strokes(data)

    if not strokes:
        return img

    points = [p for s in strokes for p in s]
    norm_p = _normalise_points(points)

    for stroke in _normalise_strokes(strokes, norm_p):
        pts = np.round(np.array(stroke)).astype(np.int32)
        for i in range(1, len(pts)):
            cv2.line(img, tuple(pts[i-1]), tuple(pts[i]), color=1.0, thickness=1, lineType=cv2.LINE_AA)
    img = cv2.GaussianBlur(img, (3, 3,), 0.5)
    if not sideways_keyboard:
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

    if img.max() > 0:
        img /= img.max()

    return img


        

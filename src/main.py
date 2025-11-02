from prediction.markov import predict_next_letter
from char_mapper import CharMapper
from vectorconvert import get_image_for_ocr
from keyboard_hooks import KeyHook
from prediction.inference import predict_letter_from_image
import math
import matplotlib

mapper = CharMapper(rotate=False)
context = ""
ocr_bias = 0.95

def add_key(key: str):
    print(f"key {key}")

def get_prediction(text_preds: dict[str, float], img_preds: dict[str, float], weight=ocr_bias) -> str:
    best = ""
    log_p_best = -math.inf

    for char in set(text_preds) | set(img_preds):
        p_text = max(text_preds.get(char, 1e-12), 1e-12)
        p_img  = max(img_preds.get(char, 1e-12), 1e-12)
        log_combined = weight * math.log(p_img) + (1 - weight) * math.log(p_text)
        if log_combined > log_p_best:
            log_p_best = log_combined
            best = char
    return best


def finish_draw(keys: list[list[str]]):
    global context
    avg = mapper.averagePoints(keys)
    img = get_image_for_ocr(avg)
    save_plot(img)
    text_predictions = predict_next_letter(context)
    img_predictions = predict_letter_from_image(img)
    print(img_predictions)

    prediction = get_prediction(text_predictions, img_predictions)
    print(prediction)
    context += prediction

def save_plot(img):
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.imshow(img)
    plt.savefig('image.png')

if __name__ == "__main__":
    hook = KeyHook(add_key, finish_draw)
    hook.start()

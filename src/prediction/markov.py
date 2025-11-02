from collections import defaultdict, Counter
import re
import numpy as np
from pathlib import Path
import pickle

_model_probs = {}
_order = 3
_model_loaded = False

_CORPUS_PATH = Path(__file__).parent / "corpus.txt"
_MODEL_PATH = Path(__file__).parent / "markov_model.pkl"

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
CHAR_TO_IDX = {c: i for i, c in enumerate(ALPHABET)}
IDX_TO_CHAR = {i: c for c, i in CHAR_TO_IDX.items()}
NUM_CHARS = len(ALPHABET)

def _test_model(test_text):
    correct_chars = 0
    total_chars = 0

    print(f"Testing {type(test_text)} chars...")

    for i in range(1, len(test_text) - _order, 10):
        if i % 500000 == 0:
            print(f"Testing char {i}")
        ctx = test_text[i:i+_order]
        true_char = test_text[i+_order]

        probs = _model_probs.get(ctx)
        if probs is None:
            continue
        if IDX_TO_CHAR[int(np.argmax(probs))] == true_char:
            correct_chars += 1
        total_chars += 1

    accuracy = correct_chars / total_chars
    print(f"Markov char-level accuracy on test: {accuracy*100:.2f}%")


def _get_corpus() -> str:
    with open(_CORPUS_PATH, "r", encoding="utf-8") as f:
        text = f.read()
    
    text = re.sub(r'\s+', ' ', text)
    text = text.strip().upper()
    return text

def _train_model():
    global _model_probs

    text = _get_corpus()
    split_idx = int(0.8 * len(text))
    train_text = text[:split_idx]
    test_text = text[split_idx:]

    counts = defaultdict(Counter)

    for i in range(len(train_text) - _order):
        context = train_text[i:i+_order]
        next_char = train_text[i+_order]
        counts[context][next_char] += 1

        if i % 1_000_000 == 0 and i > 0:
            print(f"Processed {i/1_000_000:.1f}M chars")


    print("Getting probabilities...")
    _model_probs = {}
    
    for ctx, counter in counts.items():
        arr = np.zeros(NUM_CHARS, dtype=np.float32)
        total = sum(counter.values())
        for ch, cnt in counter.items():
            arr[CHAR_TO_IDX[ch]] = cnt / total
        _model_probs[ctx] = arr

    with open(_MODEL_PATH, "wb") as f:
        pickle.dump(_model_probs, f)

    _test_model(test_text)
    
def _load_or_train_model():
    global _model_probs, _model_loaded
    try:
        with open(_MODEL_PATH, "rb") as f:
            _model_probs = pickle.load(f)
            text = _get_corpus()
            test_idx = int(0.8 * len(text))
            _test_model(text[test_idx:])
    except FileNotFoundError:
        _train_model()
    _model_loaded = True

def predict_next_letter(context: str) -> dict[str, float]:
    if not _model_loaded:
        _load_or_train_model()
    context = context.upper()[-_order:]

    for k in range(_order, 0, -1):
        ctx = context[-k:]
        if ctx in _model_probs:
            probs_array =_model_probs[ctx]
            return {IDX_TO_CHAR[i]: probs_array[i] for i in range(NUM_CHARS)}

    uniform = 1.0 / NUM_CHARS
    return {c: uniform for c in ALPHABET}

if __name__ == "__main__":
    _load_or_train_model()


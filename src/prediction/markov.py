from collections import defaultdict, Counter
import random
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

def _train_model():
    global _model_probs

    with open(_CORPUS_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    text = text.replace(" ", "")

    split_idx = int(0.8 * len(text))
    train_text = text[:split_idx]
    test_text = text[split_idx:]

    counts = {}

    for i in range(len(train_text) - _order):
        if i % 250000 == 0:
            print(f"Training char {i}")
        context = train_text[i:i+_order]
        next_char = train_text[i+_order]
        if context not in counts:
            counts[context] = np.zeros(NUM_CHARS, dtype=np.float32)
        counts[context][CHAR_TO_IDX[next_char]] += 1

    _model_probs = {ctx: arr / arr.sum() for ctx, arr in counts.items()}

    correct_chars = 0
    total_chars = 0

    for i in range(len(test_text) - _order):
        if i % 250000 == 0:
            print(f"Testing char {i}")
        ctx = test_text[i:i+_order]
        true_char = test_text[i+_order]

        probs = predict_next_letter(ctx)
        pred_char = max(probs, key=probs.get)
        
        if pred_char == true_char:
            correct_chars += 1
        total_chars += 1

    accuracy = correct_chars / total_chars
    print(f"Markov char-level accuracy on test: {accuracy*100:.2f}%")

    with open(_MODEL_PATH, "wb") as f:
        pickle.dump(_model_probs, f)

def _load_or_train_model():
    global _model_probs, _model_loaded
    try:
        with open(_MODEL_PATH, "rb") as f:
            _model_probs = pickle.load(f)
    except FileNotFoundError:
        _train_model()
    _model_loaded = True

def predict_next_letter(context: str) -> dict[str, float]:
    if not _model_loaded:
        _load_or_train_model()
    context = context.upper()[-_order:]

    probs = {}

    for k in range(_order, 0, -1):
        ctx = context[-k:]
        if ctx in _model_probs:
            probs_array =_model_probs[ctx]
            probs = {IDX_TO_CHAR[i]: probs_array[i] for i in range(NUM_CHARS)}

    if probs == {}:
        uniform = 1.0 / NUM_CHARS
        probs = {c: uniform for c in ALPHABET}
    probs[" "]=1e-12
    return probs

if __name__ == "__main__":
    _load_or_train_model()


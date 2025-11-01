from collections import defaultdict, Counter
from pathlib import Path
import pickle

_model_probs = {}
_order = 3
_model_loaded = False

_CORPUS_PATH = Path(__file__).parent / "corpus.txt"
_MODEL_PATH = Path(__file__).parent / "markov_model.pkl"


def _train_model():
    global _model_probs

    with open(_CORPUS_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    model = defaultdict(Counter)

    for i in range(len(text) - _order):
        context = text[i:i+_order]
        next_char = text[i+_order]
        model[context][next_char] += 1

    for context, counter in model.items():
        total = sum(counter.values())
        probs = {char: count / total for char, count in counter.items()}
        _model_probs[context] = probs
    

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

def predict_next_letter(context: str) -> list[tuple[str, float]]:
    if not _model_loaded:
        _load_or_train_model()
    context = context.upper()[-_order:]

    if context in _model_probs:
        probs = _model_probs[context]
    elif len(context) >= 2 and context[-2:] in _model_probs:
        probs = _model_probs[context[-2:]]
    elif len(context) >= 1 and context[-1:] in _model_probs:
        probs = _model_probs[context[-1:]]
    else:
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        probs = {c: 1/len(letters) for c in letters}
    return sorted(probs.items(), key = lambda x: x[1], reverse=True)

if __name__ == "__main__":
    while(True):
        context = input(">")
        print(predict_next_letter(context))

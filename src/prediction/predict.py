from collections import defaultdict, Counter
import pickle

model_probs = {}
order = 3

def init_model():
    with open("corpus.txt", "r", encoding="utf-8") as f:
        text = f.read()
    print(f"Corpus length: {len(text)} chars")

    # Model
    model = defaultdict(Counter)

    for i in range(len(text) - order):
        context = text[i:i+order]
        next = text[i+order]
        model[context][next] += 1

    for context, counter in model.items():
        total = sum(counter.values())
        probs = {char: count / total for char, count in counter.items()}
        model_probs[context] = probs

    with open("markov_model.pkl", "wb") as f:
        pickle.dump(model_probs, f)

def predict_next_letter(context: str, probs) -> dict[str, float]:
    context = context.upper()[-order:]
    if context in probs:
        return probs[context]
    else:
        if len(context) >= 2 and context[-2:] in model_probs:
            return probs[context[-2:]]
        elif len(context) >= 1 and context[-1:] in model_probs:
            return probs[context[-1:]]
        else:
            letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            return {c: 1/len(letters) for c in letters}


try:
    with open("markov_model.pkl", "rb") as f:
        model_probs = pickle.load(f)
except FileNotFoundError:
    init_model()


if __name__ == "__main__":
    while(True):
        context = input(">")
        print(sorted(predict_next_letter(context, model_probs)))


from prediction.markov import predict_next_letter
from charMapper import CharMapper
from vectorconvert import get_image_for_ocr

context = ""

if __name__ == "__main__":
    while(True):
        context = input(">")
        print(predict_next_letter(context))



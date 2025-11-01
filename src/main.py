from prediction.markov import predict_next_letter
from charMapper import CharMapper
from vectorconvert import get_image_for_ocr
from keyboard_hooks import start_listener

mapper = CharMapper(rotate=False)

def add_key(key: str):
    pass

def finish_draw(keys: list[list[str]]):
    avg = mapper.averagePoints(keys)
    img = get_image_for_ocr(avg)
    


start_listener(add_key, finish_draw)




import random

from reader import AbstractReader

class RandomReader(AbstractReader):

    def __next__(self):
        return round(random.random() * 5, 2)
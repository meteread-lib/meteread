from processor import AbstractProcessor
from reader import AbstractReader


class AbstractMeter():
    def __init__(self, name: str, reader: AbstractReader, processor: AbstractProcessor):
        self.name = name
        self.reader = reader
        self.processor = processor

    def __call__(self, *args, **kwargs):
        while self.processor(next(self.reader)):
            pass
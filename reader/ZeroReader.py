from reader import AbstractReader

class ZeroReader(AbstractReader):

    def __next__(self):
        return 0.0
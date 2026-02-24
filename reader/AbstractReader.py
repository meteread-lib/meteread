from abc import ABC, abstractmethod
from collections.abc import Iterator


class AbstractReader(Iterator, ABC):
    @abstractmethod
    def __next__(self):
        raise StopIteration
from abc import abstractmethod, ABC

from storage.AbstractStorage import AbstractStorage


class AbstractProcessor(ABC):
    def __init__(self, storage: AbstractStorage | None = None):
        self.storage = storage

    @abstractmethod
    def __call__(self, data) -> None:
        pass
from abc import ABC, abstractmethod
from datetime import datetime


class AbstractStorage(ABC):
    def __init__(self, measurement: str):
        self.measurement = measurement

    @abstractmethod
    def write(self, tags: dict, fields: dict, timestamp: datetime | None = None) -> None:
        pass

from abc import ABC, abstractmethod
from datetime import datetime


class AbstractStorage(ABC):
    @abstractmethod
    def write(self, measurement: str, tags: dict, fields: dict, timestamp: datetime | None = None) -> None:
        pass

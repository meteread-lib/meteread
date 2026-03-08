import logging

from processor.AbstractProcessor import AbstractProcessor
from storage.AbstractStorage import AbstractStorage

logger = logging.getLogger(__name__)


class CameraProcessor(AbstractProcessor):
    def __init__(self, storage: AbstractStorage | None = None):
        super().__init__(storage=storage)

    def __call__(self, data: dict) -> None:
        value = data["value"]
        confidence = data["confidence"]
        raw_text = data["raw_text"]

        if value is None:
            logger.warning(
                f"camera read failed: "
                f"raw_text={raw_text!r} "
                f"confidence={confidence}")
            return

        logger.info(
            f"camera value={value} "
            f"confidence={confidence:.2f} "
            f"raw={raw_text!r}")

        if self.storage:
            self.storage.write({"sn": None}, {"value": value})

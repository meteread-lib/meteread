import logging

from processor import AbstractProcessor
from storage.AbstractStorage import AbstractStorage

logger = logging.getLogger(__name__)

GAS_DEVICE_TYPE = 3


class DSMRGasProcessor(AbstractProcessor):
    def __init__(self, storage: AbstractStorage | None = None):
        super().__init__(storage=storage)

    def __call__(self, data) -> None:
        for device in data.MBUS_DEVICES:
            if device.MBUS_DEVICE_TYPE.value == GAS_DEVICE_TYPE:
                sn = device.MBUS_EQUIPMENT_IDENTIFIER.value
                reading = device.MBUS_METER_READING
                logger.info(f"gas sn={sn} reading={reading.value} {reading.unit}")
                if self.storage:
                    self.storage.write(
                        "gas",
                        {"sn": sn},
                        {"reading": reading.value},
                    )
                return

import logging

from processor import AbstractProcessor
from storage.AbstractStorage import AbstractStorage

logger = logging.getLogger(__name__)


class DSMRElectricityProcessor(AbstractProcessor):
    def __init__(self, storage: AbstractStorage | None = None):
        super().__init__(storage=storage)

    def __call__(self, data) -> None:
        sn = data.EQUIPMENT_IDENTIFIER.value
        t1 = data.ELECTRICITY_USED_TARIFF_1
        t2 = data.ELECTRICITY_USED_TARIFF_2
        current = data.CURRENT_ELECTRICITY_USAGE
        returned = data.CURRENT_ELECTRICITY_DELIVERY

        logger.info(
            f"electricity sn={sn} "
            f"t1={t1.value}{t1.unit} "
            f"t2={t2.value}{t2.unit} "
            f"now={current.value}{current.unit} "
            f"returned={returned.value}{returned.unit}"
        )

        if self.storage:
            self.storage.write(
                "electricity",
                {"sn": sn},
                {
                    "t1": t1.value,
                    "t2": t2.value,
                    "current": current.value,
                    "returned": returned.value,
                },
            )

import logging

from processor import AbstractProcessor
from storage.AbstractStorage import AbstractStorage

logger = logging.getLogger(__name__)


class DSMRElectricityProcessor(AbstractProcessor):
    def __init__(self, storage: AbstractStorage | None = None):
        super().__init__(storage=storage)

    def __call__(self, data) -> None:
        sn = data.EQUIPMENT_IDENTIFIER.value
        used_tariff_1 = data.ELECTRICITY_USED_TARIFF_1
        used_tariff_2 = data.ELECTRICITY_USED_TARIFF_2
        usage = data.CURRENT_ELECTRICITY_USAGE
        delivery = data.CURRENT_ELECTRICITY_DELIVERY

        logger.info(
            f"electricity "
            f"sn={sn} "
            f"used_tariff_1={used_tariff_1.value} {used_tariff_1.unit} "
            f"used_tariff_2={used_tariff_2.value} {used_tariff_2.unit} "
            f"usage={usage.value} {usage.unit} "
            f"delivery={delivery.value} {delivery.unit}"
        )

        if self.storage:
            self.storage.write(
                "electricity",
                {
                    "sn": sn,
                },
                {
                    "used_tariff_1": used_tariff_1.value,
                    "used_tariff_2": used_tariff_2.value,
                    "usage": usage.value,
                    "delivery": delivery.value,
                },
            )

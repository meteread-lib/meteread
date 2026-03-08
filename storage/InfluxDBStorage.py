import logging
from datetime import datetime, timezone

from influxdb_client_3 import InfluxDBClient3, Point

from storage import AbstractStorage

logger = logging.getLogger(__name__)


class InfluxDBStorage(AbstractStorage):
    def __init__(self, measurement: str, host: str, database: str, token: str = ''):
        super().__init__(measurement=measurement)
        self._client = InfluxDBClient3(host=host, database=database, token=token)

    def write(self, tags: dict, fields: dict, timestamp: datetime | None = None) -> None:
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        point = Point(self.measurement).time(timestamp)
        for key, value in tags.items():
            point = point.tag(key, value)
        for key, value in fields.items():
            point = point.field(key, value)

        self._client.write(record=point)
        logger.info(f"influxdb write: {self.measurement} {fields}")

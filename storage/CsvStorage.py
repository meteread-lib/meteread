import csv
import logging
from datetime import datetime, timezone
from pathlib import Path

from storage import AbstractStorage

logger = logging.getLogger(__name__)


class CsvStorage(AbstractStorage):
    def __init__(self, path: str):
        self.path = Path(path)

    def write(self, measurement: str, tags: dict, fields: dict, timestamp: datetime | None = None) -> None:
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        row = {"timestamp": timestamp.isoformat(), "measurement": measurement, **tags, **fields}

        write_header = not self.path.exists()
        with open(self.path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if write_header:
                writer.writeheader()
            writer.writerow(row)

        logger.info(f"csv write: {measurement} {fields}")

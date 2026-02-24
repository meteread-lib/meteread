import csv
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from storage.AbstractStorage import AbstractStorage
from storage.CsvStorage import CsvStorage
from storage.InfluxDBStorage import InfluxDBStorage

TIMESTAMP = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
MEASUREMENT = "electricity"
TAGS = {"sn": "abc123"}
FIELDS = {"t1": 1234.567, "t2": 2345.678}


class TestAbstractStorage:
    def test_cannot_instantiate(self):
        with pytest.raises(TypeError):
            AbstractStorage()

    def test_subclass_must_implement_write(self):
        class Incomplete(AbstractStorage):
            pass

        with pytest.raises(TypeError):
            Incomplete()


class TestCsvStorage:
    def test_creates_file_on_first_write(self, tmp_path):
        path = tmp_path / "readings.csv"
        CsvStorage(str(path)).write(MEASUREMENT, TAGS, FIELDS, TIMESTAMP)
        assert path.exists()

    def test_writes_header_on_first_write(self, tmp_path):
        path = tmp_path / "readings.csv"
        CsvStorage(str(path)).write(MEASUREMENT, TAGS, FIELDS, TIMESTAMP)
        with open(path) as f:
            header = f.readline().strip()
        assert header == "timestamp,measurement,sn,t1,t2"

    def test_writes_data_row(self, tmp_path):
        path = tmp_path / "readings.csv"
        CsvStorage(str(path)).write(MEASUREMENT, TAGS, FIELDS, TIMESTAMP)
        with open(path) as f:
            reader = csv.DictReader(f)
            row = next(reader)
        assert row["measurement"] == MEASUREMENT
        assert row["sn"] == "abc123"
        assert row["t1"] == "1234.567"
        assert row["t2"] == "2345.678"
        assert row["timestamp"] == TIMESTAMP.isoformat()

    def test_appends_without_repeating_header(self, tmp_path):
        path = tmp_path / "readings.csv"
        storage = CsvStorage(str(path))
        storage.write(MEASUREMENT, TAGS, FIELDS, TIMESTAMP)
        storage.write(MEASUREMENT, TAGS, FIELDS, TIMESTAMP)
        with open(path) as f:
            lines = f.readlines()
        assert len(lines) == 3  # 1 header + 2 data rows

    def test_uses_current_time_when_timestamp_is_none(self, tmp_path):
        path = tmp_path / "readings.csv"
        before = datetime.now(timezone.utc)
        CsvStorage(str(path)).write(MEASUREMENT, TAGS, FIELDS)
        after = datetime.now(timezone.utc)
        with open(path) as f:
            row = next(csv.DictReader(f))
        written = datetime.fromisoformat(row["timestamp"])
        assert before <= written <= after

    def test_returns_none(self, tmp_path):
        path = tmp_path / "readings.csv"
        result = CsvStorage(str(path)).write(MEASUREMENT, TAGS, FIELDS, TIMESTAMP)
        assert result is None


class TestInfluxDBStorage:
    @pytest.fixture
    def mock_client(self):
        with patch("storage.InfluxDBStorage.InfluxDBClient3") as mock:
            yield mock

    @pytest.fixture
    def storage(self, mock_client):
        return InfluxDBStorage(
            host="http://localhost:8086",
            token="my-token",
            database="my-database",
        )

    def test_creates_client_with_correct_params(self, mock_client):
        InfluxDBStorage(host="http://host:8086", token="tok", database="db")
        mock_client.assert_called_once_with(host="http://host:8086", token="tok", database="db")

    def test_write_calls_client_write(self, storage, mock_client):
        storage.write(MEASUREMENT, TAGS, FIELDS, TIMESTAMP)
        mock_client.return_value.write.assert_called_once()

    def test_write_point_has_correct_measurement(self, storage, mock_client):
        with patch("storage.InfluxDBStorage.Point") as mock_point:
            mock_point.return_value.time.return_value = mock_point.return_value
            mock_point.return_value.tag.return_value = mock_point.return_value
            mock_point.return_value.field.return_value = mock_point.return_value
            storage.write(MEASUREMENT, TAGS, FIELDS, TIMESTAMP)
        mock_point.assert_called_once_with(MEASUREMENT)

    def test_write_point_has_correct_tags(self, storage, mock_client):
        with patch("storage.InfluxDBStorage.Point") as mock_point:
            mock_point.return_value.time.return_value = mock_point.return_value
            mock_point.return_value.tag.return_value = mock_point.return_value
            mock_point.return_value.field.return_value = mock_point.return_value
            storage.write(MEASUREMENT, TAGS, FIELDS, TIMESTAMP)
        mock_point.return_value.tag.assert_called_once_with("sn", "abc123")

    def test_write_point_has_correct_fields(self, storage, mock_client):
        with patch("storage.InfluxDBStorage.Point") as mock_point:
            mock_point.return_value.time.return_value = mock_point.return_value
            mock_point.return_value.tag.return_value = mock_point.return_value
            mock_point.return_value.field.return_value = mock_point.return_value
            storage.write(MEASUREMENT, TAGS, FIELDS, TIMESTAMP)
        calls = {call.args for call in mock_point.return_value.field.call_args_list}
        assert calls == {("t1", 1234.567), ("t2", 2345.678)}

    def test_write_point_has_correct_timestamp(self, storage, mock_client):
        with patch("storage.InfluxDBStorage.Point") as mock_point:
            mock_point.return_value.time.return_value = mock_point.return_value
            mock_point.return_value.tag.return_value = mock_point.return_value
            mock_point.return_value.field.return_value = mock_point.return_value
            storage.write(MEASUREMENT, TAGS, FIELDS, TIMESTAMP)
        mock_point.return_value.time.assert_called_once_with(TIMESTAMP)

    def test_uses_current_time_when_timestamp_is_none(self, storage, mock_client):
        with patch("storage.InfluxDBStorage.Point") as mock_point:
            mock_point.return_value.time.return_value = mock_point.return_value
            mock_point.return_value.tag.return_value = mock_point.return_value
            mock_point.return_value.field.return_value = mock_point.return_value
            before = datetime.now(timezone.utc)
            storage.write(MEASUREMENT, TAGS, FIELDS)
            after = datetime.now(timezone.utc)
        used_ts = mock_point.return_value.time.call_args.args[0]
        assert before <= used_ts <= after

    def test_returns_none(self, storage, mock_client):
        result = storage.write(MEASUREMENT, TAGS, FIELDS, TIMESTAMP)
        assert result is None

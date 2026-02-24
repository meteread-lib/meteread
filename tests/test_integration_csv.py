import csv
from decimal import Decimal

import pytest

from meter import GenericMeter
from processor import ChainProcessor, DSMRElectricityProcessor, DSMRGasProcessor
from reader import DSMRv5RawReader
from storage import CsvStorage


class TestElectricityCsvPipeline:
    @pytest.fixture
    def csv_row(self, tmp_path, telegram):
        path = tmp_path / "readings.csv"
        DSMRElectricityProcessor(storage=CsvStorage(str(path)))(telegram)
        with open(path) as f:
            return next(csv.DictReader(f))

    def test_measurement(self, csv_row):
        assert csv_row["measurement"] == "electricity"

    def test_serial_number(self, csv_row):
        assert csv_row["sn"] == "4530303334303034363639353537343136"

    def test_tariff_1(self, csv_row):
        assert Decimal(csv_row["t1"]) == Decimal("1234.567")

    def test_tariff_2(self, csv_row):
        assert Decimal(csv_row["t2"]) == Decimal("2345.678")

    def test_current_usage(self, csv_row):
        assert Decimal(csv_row["current"]) == Decimal("1.500")

    def test_returned(self, csv_row):
        assert Decimal(csv_row["returned"]) == Decimal("0.000")


class TestGasCsvPipeline:
    @pytest.fixture
    def csv_row(self, tmp_path, telegram):
        path = tmp_path / "readings.csv"
        DSMRGasProcessor(storage=CsvStorage(str(path)))(telegram)
        with open(path) as f:
            return next(csv.DictReader(f))

    def test_measurement(self, csv_row):
        assert csv_row["measurement"] == "gas"

    def test_serial_number(self, csv_row):
        assert csv_row["sn"] == "4730303233353631323930333635383137"

    def test_reading(self, csv_row):
        assert Decimal(csv_row["reading"]) == Decimal("1234.567")


class TestMeterCsvPipeline:
    def test_meter_creates_csv(self, tmp_path, raw_telegram_v5):
        path = tmp_path / "readings.csv"
        meter = GenericMeter(
            name='test',
            reader=DSMRv5RawReader(raw=raw_telegram_v5),
            processor=DSMRElectricityProcessor(storage=CsvStorage(str(path))),
        )
        meter()
        assert path.exists()

    def test_meter_writes_one_row(self, tmp_path, raw_telegram_v5):
        path = tmp_path / "readings.csv"
        meter = GenericMeter(
            name='test',
            reader=DSMRv5RawReader(raw=raw_telegram_v5),
            processor=DSMRElectricityProcessor(storage=CsvStorage(str(path))),
        )
        meter()
        with open(path) as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 1
        assert rows[0]["measurement"] == "electricity"

    def test_repeated_meter_calls_append_rows(self, tmp_path, raw_telegram_v5):
        path = tmp_path / "readings.csv"
        storage = CsvStorage(str(path))
        meter = GenericMeter(
            name='test',
            reader=DSMRv5RawReader(raw=raw_telegram_v5),
            processor=DSMRElectricityProcessor(storage=storage),
        )
        meter()
        meter()
        with open(path) as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 2

    def test_chain_writes_electricity_and_gas(self, tmp_path, raw_telegram_v5):
        elec_path = tmp_path / "electricity.csv"
        gas_path = tmp_path / "gas.csv"
        meter = GenericMeter(
            name='test',
            reader=DSMRv5RawReader(raw=raw_telegram_v5),
            processor=ChainProcessor(
                DSMRElectricityProcessor(storage=CsvStorage(str(elec_path))),
                DSMRGasProcessor(storage=CsvStorage(str(gas_path))),
            ),
        )
        meter()
        with open(elec_path) as f:
            assert next(csv.DictReader(f))["measurement"] == "electricity"
        with open(gas_path) as f:
            assert next(csv.DictReader(f))["measurement"] == "gas"

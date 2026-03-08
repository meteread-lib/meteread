import socket

import pytest
from influxdb_client_3 import InfluxDBClient3

from processor import DSMRElectricityProcessor, DSMRGasProcessor
from storage import InfluxDBStorage

INFLUXDB_HOST = 'http://localhost:8181'
INFLUXDB_TOKEN = ''
INFLUXDB_DATABASE = 'meteread'

ELECTRICITY_SN = '4530303334303034363639353537343136'
GAS_SN = '4730303233353631323930333635383137'


def _influxdb_reachable():
    try:
        sock = socket.socket()
        sock.settimeout(1)
        sock.connect(('localhost', 8181))
        sock.close()
        return True
    except (socket.error, OSError):
        return False


pytestmark = pytest.mark.skipif(
    not _influxdb_reachable(),
    reason="InfluxDB not reachable at localhost:8181",
)


@pytest.fixture
def storage():
    return InfluxDBStorage(measurement="electricity", host=INFLUXDB_HOST, token=INFLUXDB_TOKEN, database=INFLUXDB_DATABASE)



@pytest.fixture
def client():
    return InfluxDBClient3(host=INFLUXDB_HOST, token=INFLUXDB_TOKEN, database=INFLUXDB_DATABASE)


class TestElectricityInfluxDBPipeline:
    def test_writes_electricity_measurement(self, storage, client, telegram):
        DSMRElectricityProcessor(storage=storage)(telegram)
        table = client.query(
            f"SELECT * FROM electricity WHERE sn = '{ELECTRICITY_SN}' ORDER BY time DESC LIMIT 1"
        )
        assert table.num_rows >= 1

    def test_writes_tariff_1(self, storage, client, telegram):
        DSMRElectricityProcessor(storage=storage)(telegram)
        table = client.query(
            f"SELECT used_tariff_1 FROM electricity WHERE sn = '{ELECTRICITY_SN}' ORDER BY time DESC LIMIT 1"
        )
        assert pytest.approx(table.column('used_tariff_1').to_pylist()[0], abs=0.001) == 1234.567

    def test_writes_tariff_2(self, storage, client, telegram):
        DSMRElectricityProcessor(storage=storage)(telegram)
        table = client.query(
            f"SELECT used_tariff_2 FROM electricity WHERE sn = '{ELECTRICITY_SN}' ORDER BY time DESC LIMIT 1"
        )
        assert pytest.approx(table.column('used_tariff_2').to_pylist()[0], abs=0.001) == 2345.678

    def test_writes_current(self, storage, client, telegram):
        DSMRElectricityProcessor(storage=storage)(telegram)
        table = client.query(
            f"SELECT usage FROM electricity WHERE sn = '{ELECTRICITY_SN}' ORDER BY time DESC LIMIT 1"
        )
        assert pytest.approx(table.column('usage').to_pylist()[0], abs=0.001) == 1.500

    def test_writes_returned(self, storage, client, telegram):
        DSMRElectricityProcessor(storage=storage)(telegram)
        table = client.query(
            f"SELECT delivery FROM electricity WHERE sn = '{ELECTRICITY_SN}' ORDER BY time DESC LIMIT 1"
        )
        assert pytest.approx(table.column('delivery').to_pylist()[0], abs=0.001) == 0.000


class TestGasInfluxDBPipeline:
    def test_writes_gas_measurement(self, storage, client, telegram):
        DSMRGasProcessor(storage=storage)(telegram)
        table = client.query(
            f"SELECT * FROM gas WHERE sn = '{GAS_SN}' ORDER BY time DESC LIMIT 1"
        )
        assert table.num_rows >= 1

    def test_writes_reading(self, storage, client, telegram):
        DSMRGasProcessor(storage=storage)(telegram)
        table = client.query(
            f"SELECT reading FROM gas WHERE sn = '{GAS_SN}' ORDER BY time DESC LIMIT 1"
        )
        assert pytest.approx(table.column('reading').to_pylist()[0], abs=0.001) == 1234.567

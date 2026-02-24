from decimal import Decimal
from unittest.mock import MagicMock

from processor.NoneProcessor import NoneProcessor
from processor.PassProcessor import PassProcessor
from processor.DSMRElectricityProcessor import DSMRElectricityProcessor
from processor.DSMRGasProcessor import DSMRGasProcessor
from processor.ChainProcessor import ChainProcessor


class TestNoneProcessor:
    def test_returns_none(self):
        processor = NoneProcessor()
        assert processor(42) is None

    def test_returns_none_for_string_input(self):
        processor = NoneProcessor()
        assert processor("hello") is None

    def test_returns_none_for_none_input(self):
        processor = NoneProcessor()
        assert processor(None) is None

    def test_is_callable(self):
        processor = NoneProcessor()
        assert callable(processor)


class TestPassProcessor:
    def test_returns_none(self):
        processor = PassProcessor()
        result = processor(42)
        assert result is None

    def test_returns_none_for_string_input(self):
        processor = PassProcessor()
        assert processor("data") is None

    def test_returns_none_for_none_input(self):
        processor = PassProcessor()
        assert processor(None) is None

    def test_is_callable(self):
        processor = PassProcessor()
        assert callable(processor)


class TestDSMRElectricityProcessor:
    def test_returns_none(self, telegram):
        assert DSMRElectricityProcessor()(telegram) is None

    def test_prints_electricity_line(self, telegram, caplog):
        DSMRElectricityProcessor()(telegram)
        assert caplog.messages[0].startswith('electricity')

    def test_prints_serial_number(self, telegram, caplog):
        DSMRElectricityProcessor()(telegram)
        assert 'sn=4530303334303034363639353537343136' in caplog.messages[0]

    def test_prints_tariff_1(self, telegram, caplog):
        DSMRElectricityProcessor()(telegram)
        assert 't1=1234.567kWh' in caplog.messages[0]

    def test_prints_tariff_2(self, telegram, caplog):
        DSMRElectricityProcessor()(telegram)
        assert 't2=2345.678kWh' in caplog.messages[0]

    def test_prints_current_usage(self, telegram, caplog):
        DSMRElectricityProcessor()(telegram)
        assert 'now=1.500kW' in caplog.messages[0]

    def test_prints_current_delivery(self, telegram, caplog):
        DSMRElectricityProcessor()(telegram)
        assert 'returned=0.000kW' in caplog.messages[0]

    def test_writes_to_storage(self, telegram):
        storage = MagicMock()
        DSMRElectricityProcessor(storage=storage)(telegram)
        storage.write.assert_called_once_with(
            "electricity",
            {"sn": "4530303334303034363639353537343136"},
            {
                "t1": Decimal("1234.567"),
                "t2": Decimal("2345.678"),
                "current": Decimal("1.500"),
                "returned": Decimal("0.000"),
            },
        )

    def test_does_not_write_to_storage_when_none(self, telegram):
        storage = MagicMock()
        DSMRElectricityProcessor()(telegram)
        storage.write.assert_not_called()


class TestDSMRGasProcessor:
    def test_returns_none(self, telegram):
        assert DSMRGasProcessor()(telegram) is None

    def test_prints_gas_line(self, telegram, caplog):
        DSMRGasProcessor()(telegram)
        assert caplog.messages[0].startswith('gas')

    def test_prints_serial_number(self, telegram, caplog):
        DSMRGasProcessor()(telegram)
        assert 'sn=4730303233353631323930333635383137' in caplog.messages[0]

    def test_prints_reading(self, telegram, caplog):
        DSMRGasProcessor()(telegram)
        assert 'reading=1234.567 m3' in caplog.messages[0]

    def test_writes_to_storage(self, telegram):
        storage = MagicMock()
        DSMRGasProcessor(storage=storage)(telegram)
        storage.write.assert_called_once_with(
            "gas",
            {"sn": "4730303233353631323930333635383137"},
            {"reading": Decimal("1234.567")},
        )

    def test_does_not_write_to_storage_when_none(self, telegram):
        storage = MagicMock()
        DSMRGasProcessor()(telegram)
        storage.write.assert_not_called()

    def test_no_output_for_non_gas_device(self, caplog):
        water_device = MagicMock()
        water_device.MBUS_DEVICE_TYPE.value = 7
        mock_telegram = MagicMock()
        mock_telegram.MBUS_DEVICES = [water_device]
        DSMRGasProcessor()(mock_telegram)
        assert caplog.messages == []


class TestChainProcessor:
    def test_calls_all_processors(self):
        a, b, c = MagicMock(), MagicMock(), MagicMock()
        ChainProcessor(a, b, c)('data')
        a.assert_called_once_with('data')
        b.assert_called_once_with('data')
        c.assert_called_once_with('data')

    def test_calls_in_order(self):
        order = []
        a = MagicMock(side_effect=lambda d: order.append('a'))
        b = MagicMock(side_effect=lambda d: order.append('b'))
        ChainProcessor(a, b)('data')
        assert order == ['a', 'b']

    def test_returns_none(self):
        assert ChainProcessor(MagicMock())('data') is None

    def test_empty_chain(self):
        assert ChainProcessor()('data') is None

    def test_passes_same_data_to_all(self):
        received = []
        p = MagicMock(side_effect=lambda d: received.append(d))
        obj = object()
        ChainProcessor(p, p)(obj)
        assert received == [obj, obj]

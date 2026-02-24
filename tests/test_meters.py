from unittest.mock import MagicMock, call

from meter.GenericMeter import GenericMeter


class TestGenericMeter:
    def test_calls_reader_and_processor_once(self):
        """Since processor returns None (falsy), the while loop exits after one iteration."""
        reader = MagicMock()
        reader.__next__ = MagicMock(return_value=42.0)
        processor = MagicMock(return_value=None)

        meter = GenericMeter(name="test", reader=reader, processor=processor)
        meter()

        reader.__next__.assert_called_once()
        processor.assert_called_once_with(42.0)

    def test_stores_name(self):
        reader = MagicMock()
        processor = MagicMock()
        meter = GenericMeter(name="electricity", reader=reader, processor=processor)
        assert meter.name == "electricity"

    def test_stores_reader_and_processor(self):
        reader = MagicMock()
        processor = MagicMock()
        meter = GenericMeter(name="test", reader=reader, processor=processor)
        assert meter.reader is reader
        assert meter.processor is processor

    def test_processor_receives_reader_value(self):
        reader = MagicMock()
        reader.__next__ = MagicMock(return_value=99.5)
        processor = MagicMock(return_value=None)

        meter = GenericMeter(name="test", reader=reader, processor=processor)
        meter()

        processor.assert_called_once_with(99.5)

    def test_loop_exits_when_processor_returns_none(self):
        """The while loop condition is falsy when processor returns None,
        so only one read happens per meter call."""
        reader = MagicMock()
        reader.__next__ = MagicMock(return_value=1.0)
        processor = MagicMock(return_value=None)

        meter = GenericMeter(name="test", reader=reader, processor=processor)
        meter()

        assert reader.__next__.call_count == 1
        assert processor.call_count == 1

    def test_loop_continues_while_processor_returns_truthy(self):
        """If processor returns truthy values, the loop continues reading."""
        reader = MagicMock()
        reader.__next__ = MagicMock(side_effect=[1.0, 2.0, 3.0])
        processor = MagicMock(side_effect=[True, True, None])

        meter = GenericMeter(name="test", reader=reader, processor=processor)
        meter()

        assert reader.__next__.call_count == 3
        assert processor.call_args_list == [call(1.0), call(2.0), call(3.0)]

    def test_can_be_called_multiple_times(self):
        reader = MagicMock()
        reader.__next__ = MagicMock(return_value=0.0)
        processor = MagicMock(return_value=None)

        meter = GenericMeter(name="test", reader=reader, processor=processor)
        meter()
        meter()
        meter()

        assert reader.__next__.call_count == 3
        assert processor.call_count == 3

    def test_propagates_reader_exception(self):
        reader = MagicMock()
        reader.__next__ = MagicMock(side_effect=StopIteration)
        processor = MagicMock(return_value=None)

        meter = GenericMeter(name="test", reader=reader, processor=processor)
        try:
            meter()
            assert False, "Expected StopIteration"
        except StopIteration:
            pass

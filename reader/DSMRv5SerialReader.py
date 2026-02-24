from reader import AbstractReader
from dsmr_parser import telegram_specifications
from dsmr_parser.clients import SerialReader, SERIAL_SETTINGS_V5

class DSMRv5SerialReader(AbstractReader):
    def __init__(self, device: str = '/dev/ttyUSB0'):
        self.reader = SerialReader(
            device=device,
            serial_settings=SERIAL_SETTINGS_V5,
            telegram_specification=telegram_specifications.V5
        )
        self.iterator = self.reader.read_as_object()

    def __next__(self):
        return next(self.iterator)

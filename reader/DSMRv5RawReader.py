from dsmr_parser import telegram_specifications
from dsmr_parser.parsers import TelegramParser
from reader import AbstractReader


class DSMRv5RawReader(AbstractReader):
    def __init__(self, raw: str):
        self._telegram = TelegramParser(telegram_specifications.V5, apply_checksum_validation=False).parse(raw)

    def __next__(self):
        return self._telegram

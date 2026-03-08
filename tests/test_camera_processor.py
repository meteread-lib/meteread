from unittest.mock import MagicMock
import logging

import pytest

from processor.CameraProcessor import CameraProcessor


GOOD_READING = {"value": 12345.678, "confidence": 0.91, "raw_text": "12345.678"}
FAILED_READING = {"value": None, "confidence": 0.0, "raw_text": ""}


class TestCameraProcessorInit:
    def test_default_storage_is_none(self):
        p = CameraProcessor()
        assert p.storage is None

    def test_accepts_storage(self):
        storage = MagicMock()
        p = CameraProcessor(storage=storage)
        assert p.storage is storage


class TestCameraProcessorCall:
    def test_returns_none(self):
        p = CameraProcessor()
        assert p(GOOD_READING) is None

    def test_logs_value_and_confidence(self, caplog):
        p = CameraProcessor()
        with caplog.at_level(logging.INFO):
            p(GOOD_READING)
        assert "12345.678" in caplog.text
        assert "0.91" in caplog.text

    def test_writes_to_storage_when_set(self):
        storage = MagicMock()
        p = CameraProcessor(storage=storage)
        p(GOOD_READING)
        storage.write.assert_called_once_with(
            "water",
            {},
            {"value": 12345.678},
        )

    def test_no_storage_write_when_none(self):
        storage = MagicMock()
        p = CameraProcessor()
        p(GOOD_READING)
        storage.write.assert_not_called()

    def test_skips_storage_write_on_failed_read(self):
        storage = MagicMock()
        p = CameraProcessor(storage=storage)
        p(FAILED_READING)
        storage.write.assert_not_called()

    def test_logs_warning_on_failed_read(self, caplog):
        p = CameraProcessor()
        with caplog.at_level(logging.WARNING):
            p(FAILED_READING)
        assert "failed" in caplog.text.lower() or "none" in caplog.text.lower()

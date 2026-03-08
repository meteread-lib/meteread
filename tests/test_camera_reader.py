import numpy as np
import pytest
from unittest.mock import patch, MagicMock

from reader.CameraReader import CameraReader


def _make_frame(text: str, width=200, height=60) -> np.ndarray:
    """Create a white image with black text for OCR testing."""
    import cv2
    img = np.ones((height, width, 3), dtype=np.uint8) * 255
    cv2.putText(img, text, (10, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 3)
    return img


class TestCameraReaderInit:
    def test_default_device_is_zero(self):
        reader = CameraReader()
        assert reader.device == 0

    def test_custom_device(self):
        reader = CameraReader(device=2)
        assert reader.device == 2

    def test_default_roi_is_none(self):
        reader = CameraReader()
        assert reader.roi is None

    def test_custom_roi(self):
        reader = CameraReader(roi=(10, 20, 100, 50))
        assert reader.roi == (10, 20, 100, 50)

    def test_is_iterator(self):
        reader = CameraReader()
        assert iter(reader) is reader


class TestCameraReaderProcessFrame:
    def test_returns_dict_with_required_keys(self):
        reader = CameraReader()
        frame = _make_frame("12345")
        result = reader._process_frame(frame)
        assert set(result.keys()) == {"value", "confidence", "raw_text"}

    def test_parses_integer_digits(self):
        reader = CameraReader()
        frame = _make_frame("12345")
        result = reader._process_frame(frame)
        assert result["value"] == 12345.0

    def test_parses_decimal_digits(self):
        reader = CameraReader()
        frame = _make_frame("123.45")
        result = reader._process_frame(frame)
        assert result["value"] == 123.45

    def test_returns_none_value_for_empty_image(self):
        reader = CameraReader()
        # All-black image — no digits
        frame = np.zeros((60, 200, 3), dtype=np.uint8)
        result = reader._process_frame(frame)
        assert result["value"] is None

    def test_returns_zero_confidence_for_failed_read(self):
        reader = CameraReader()
        frame = np.zeros((60, 200, 3), dtype=np.uint8)
        result = reader._process_frame(frame)
        assert result["confidence"] == 0.0

    def test_raw_text_is_string(self):
        reader = CameraReader()
        frame = _make_frame("99")
        result = reader._process_frame(frame)
        assert isinstance(result["raw_text"], str)


class TestCameraReaderROI:
    def test_roi_crops_frame_before_processing(self):
        reader = CameraReader(roi=(0, 0, 100, 60))
        frame = _make_frame("12345", width=200, height=60)
        original = reader._process_frame
        received_frames = []

        def capturing_process(f):
            received_frames.append(f)
            return original(f)

        reader._process_frame = capturing_process
        with patch.object(reader, "_capture_frame", return_value=frame):
            next(reader)

        assert received_frames[0].shape[1] == 100  # width cropped to 100


class TestCameraReaderNext:
    def test_next_calls_capture_frame(self):
        reader = CameraReader()
        frame = _make_frame("42")
        with patch.object(reader, "_capture_frame", return_value=frame) as mock_cap:
            next(reader)
        mock_cap.assert_called_once()

    def test_next_returns_dict(self):
        reader = CameraReader()
        frame = _make_frame("42")
        with patch.object(reader, "_capture_frame", return_value=frame):
            result = next(reader)
        assert isinstance(result, dict)
        assert "value" in result

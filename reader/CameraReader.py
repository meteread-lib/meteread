import re

import cv2
import numpy as np
import pytesseract

from reader.AbstractReader import AbstractReader


class CameraReader(AbstractReader):
    def __init__(self, device: int = 0, roi: tuple[int, int, int, int] | None = None):
        self.device = device
        self.roi = roi

    def _capture_frame(self) -> np.ndarray:
        cap = cv2.VideoCapture(self.device)
        try:
            ret, frame = cap.read()
            if not ret:
                raise RuntimeError(f"Failed to capture frame from device {self.device}")
            return frame
        finally:
            cap.release()

    def _process_frame(self, frame: np.ndarray) -> dict:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        config = "--psm 7 -c tessedit_char_whitelist=0123456789."
        data = pytesseract.image_to_data(thresh, config=config, output_type=pytesseract.Output.DICT)

        raw_text = " ".join(t for t in data["text"] if t.strip())
        confidences = [int(c) for c, t in zip(data["conf"], data["text"]) if t.strip() and int(c) > 0]
        confidence = (sum(confidences) / len(confidences) / 100.0) if confidences else 0.0

        match = re.search(r"\d+(?:\.\d+)?", raw_text)
        value = float(match.group()) if match else None
        if value is None:
            confidence = 0.0

        return {"value": value, "confidence": confidence, "raw_text": raw_text}

    def __next__(self) -> dict:
        frame = self._capture_frame()
        if self.roi:
            x, y, w, h = self.roi
            frame = frame[y:y + h, x:x + w]
        return self._process_frame(frame)

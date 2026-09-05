from dataclasses import dataclass
from time import perf_counter

import cv2
import numpy as np


@dataclass
class FrameAnalytics:
    width: int
    height: int
    fps: float
    brightness: float
    edge_density: float


class CameraProcessor:
    def __init__(self, source=0):
        self.source = source
        self.capture = None
        self._last_frame_at = None

    def open(self):
        self.capture = cv2.VideoCapture(self.source)
        if not self.capture.isOpened():
            raise RuntimeError(f"Could not open camera source: {self.source}")

    def read(self):
        if self.capture is None:
            self.open()

        ok, frame = self.capture.read()
        if not ok:
            raise RuntimeError("Could not read camera frame.")

        now = perf_counter()
        fps = 0.0
        if self._last_frame_at is not None:
            delta = now - self._last_frame_at
            if delta > 0:
                fps = 1.0 / delta
        self._last_frame_at = now

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = float(np.mean(gray))
        edges = cv2.Canny(gray, 100, 200)
        edge_density = float(np.count_nonzero(edges) / edges.size)

        analytics = FrameAnalytics(
            width=frame.shape[1],
            height=frame.shape[0],
            fps=round(fps, 2),
            brightness=round(brightness, 2),
            edge_density=round(edge_density, 4),
        )
        return frame, analytics

    def close(self):
        if self.capture is not None:
            self.capture.release()
            self.capture = None

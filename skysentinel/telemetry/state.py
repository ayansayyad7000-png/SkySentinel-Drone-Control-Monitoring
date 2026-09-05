from copy import deepcopy
from threading import Lock

from skysentinel.models import Telemetry


class TelemetryState:
    def __init__(self):
        self._lock = Lock()
        self._data = Telemetry()

    def update(self, **changes) -> None:
        with self._lock:
            for key, value in changes.items():
                if hasattr(self._data, key):
                    setattr(self._data, key, value)

    def snapshot(self) -> Telemetry:
        with self._lock:
            return deepcopy(self._data)

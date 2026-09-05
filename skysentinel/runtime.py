import logging
import threading
from time import sleep

from skysentinel.mavlink.client import MavlinkClient
from skysentinel.mavlink.controller import DroneController
from skysentinel.telemetry.health import evaluate_health
from skysentinel.telemetry.recorder import FlightRecorder
from skysentinel.telemetry.state import TelemetryState

logger = logging.getLogger(__name__)


class DroneRuntime:
    def __init__(self):
        self.state = TelemetryState()
        self.client = MavlinkClient(self.state)
        self.controller = DroneController(self.client)
        self.recorder = FlightRecorder()
        self._stop = threading.Event()
        self._thread = None
        self._record_tick = 0

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="mavlink-runtime")
        self._thread.start()

    def _run(self):
        while not self._stop.is_set():
            try:
                if self.client.connection is None:
                    self.client.connect()

                updated = self.client.read_once()
                if updated:
                    self._record_tick += 1
                    if self._record_tick >= 5:
                        snapshot = self.state.snapshot()
                        self.recorder.record_telemetry(snapshot)
                        self._record_tick = 0
                else:
                    sleep(0.02)

            except Exception as exc:
                logger.warning("MAVLink runtime error: %s", exc)
                self.state.update(connected=False)
                self.client.close()
                sleep(2)

    def telemetry_payload(self):
        telemetry = self.state.snapshot()
        alerts = evaluate_health(telemetry)
        return {
            "telemetry": telemetry.to_dict(),
            "alerts": [a.to_dict() for a in alerts],
        }

    def stop(self):
        self._stop.set()
        self.client.close()


runtime = DroneRuntime()

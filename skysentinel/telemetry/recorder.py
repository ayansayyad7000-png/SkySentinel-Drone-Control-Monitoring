import csv
import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from threading import Lock

from skysentinel.config import settings
from skysentinel.models import HealthAlert, Telemetry


class FlightRecorder:
    def __init__(self):
        settings.log_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_path = settings.log_dir / f"flight_{stamp}.csv"
        self.events_path = settings.log_dir / f"events_{stamp}.jsonl"
        self._lock = Lock()
        self._header_written = False

    def record_telemetry(self, telemetry: Telemetry) -> None:
        row = asdict(telemetry)
        with self._lock:
            with self.csv_path.open("a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(row.keys()))
                if not self._header_written:
                    writer.writeheader()
                    self._header_written = True
                writer.writerow(row)

    def record_event(self, kind: str, payload: dict) -> None:
        event = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "kind": kind,
            "payload": payload,
        }
        with self._lock:
            with self.events_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")

    def record_alerts(self, alerts: list[HealthAlert]) -> None:
        for alert in alerts:
            self.record_event("health_alert", alert.to_dict())

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    mavlink_connection: str = os.getenv("MAVLINK_CONNECTION", "udp:127.0.0.1:14550")
    mavlink_baud: int = int(os.getenv("MAVLINK_BAUD", "57600"))
    allow_actuation: bool = _as_bool(os.getenv("ALLOW_ACTUATION", "false"))
    max_takeoff_alt_m: float = float(os.getenv("MAX_TAKEOFF_ALT_M", "20"))
    low_battery_percent: int = int(os.getenv("LOW_BATTERY_PERCENT", "25"))
    critical_battery_percent: int = int(os.getenv("CRITICAL_BATTERY_PERCENT", "15"))
    max_altitude_warning_m: float = float(os.getenv("MAX_ALTITUDE_WARNING_M", "120"))
    heartbeat_stale_seconds: float = float(os.getenv("HEARTBEAT_STALE_SECONDS", "5"))
    camera_source: int = int(os.getenv("CAMERA_SOURCE", "0"))
    enable_camera: bool = _as_bool(os.getenv("ENABLE_CAMERA", "false"))
    log_dir: Path = Path(os.getenv("LOG_DIR", "logs"))


settings = Settings()

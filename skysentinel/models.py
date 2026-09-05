from dataclasses import asdict, dataclass, field
from time import time
from typing import Any


@dataclass
class Telemetry:
    connected: bool = False
    timestamp: float = field(default_factory=time)
    last_heartbeat_at: float | None = None
    system_id: int | None = None
    component_id: int | None = None
    armed: bool = False
    flight_mode: str = "UNKNOWN"
    system_status: int | None = None

    latitude: float | None = None
    longitude: float | None = None
    altitude_msl_m: float | None = None
    relative_altitude_m: float | None = None
    heading_deg: float | None = None

    groundspeed_m_s: float | None = None
    airspeed_m_s: float | None = None
    climb_m_s: float | None = None

    roll_deg: float | None = None
    pitch_deg: float | None = None
    yaw_deg: float | None = None

    gps_fix_type: int | None = None
    gps_satellites: int | None = None
    gps_hdop: float | None = None

    battery_voltage_v: float | None = None
    battery_current_a: float | None = None
    battery_percent: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class HealthAlert:
    code: str
    level: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)

from time import time

from skysentinel.config import settings
from skysentinel.models import HealthAlert, Telemetry


def evaluate_health(t: Telemetry) -> list[HealthAlert]:
    alerts: list[HealthAlert] = []

    if not t.connected:
        alerts.append(HealthAlert("DISCONNECTED", "critical", "No MAVLink vehicle connection."))

    if t.last_heartbeat_at is not None:
        age = time() - t.last_heartbeat_at
        if age > settings.heartbeat_stale_seconds:
            alerts.append(
                HealthAlert(
                    "HEARTBEAT_STALE",
                    "critical",
                    f"Heartbeat has been stale for {age:.1f} seconds.",
                )
            )

    if t.battery_percent is not None:
        if t.battery_percent <= settings.critical_battery_percent:
            alerts.append(
                HealthAlert(
                    "CRITICAL_BATTERY",
                    "critical",
                    f"Battery is critically low at {t.battery_percent}%.",
                )
            )
        elif t.battery_percent <= settings.low_battery_percent:
            alerts.append(
                HealthAlert(
                    "LOW_BATTERY",
                    "warning",
                    f"Battery is low at {t.battery_percent}%.",
                )
            )

    if t.gps_fix_type is not None and t.gps_fix_type < 3:
        alerts.append(
            HealthAlert(
                "GPS_FIX_WEAK",
                "warning",
                f"GPS fix type is {t.gps_fix_type}; 3D fix is recommended.",
            )
        )

    if t.gps_satellites is not None and t.gps_satellites < 8:
        alerts.append(
            HealthAlert(
                "GPS_SATELLITES_LOW",
                "warning",
                f"Only {t.gps_satellites} GPS satellites are visible.",
            )
        )

    if (
        t.relative_altitude_m is not None
        and t.relative_altitude_m > settings.max_altitude_warning_m
    ):
        alerts.append(
            HealthAlert(
                "ALTITUDE_LIMIT_WARNING",
                "warning",
                f"Relative altitude is {t.relative_altitude_m:.1f} m.",
            )
        )

    return alerts

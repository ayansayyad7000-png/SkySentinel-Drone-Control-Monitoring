import math
from time import time


def radians_to_degrees(value: float | None) -> float | None:
    if value is None:
        return None
    return round(math.degrees(value), 2)


def parse_mavlink_message(msg, mode_resolver=None) -> dict:
    """
    Convert selected pymavlink messages into normalized telemetry fields.
    Returns an empty dict for messages this project does not consume.
    """
    msg_type = msg.get_type()
    data: dict = {"timestamp": time()}

    if msg_type == "HEARTBEAT":
        mode = "UNKNOWN"
        if mode_resolver:
            try:
                mode = mode_resolver(msg) or "UNKNOWN"
            except Exception:
                pass

        armed = bool(
            getattr(msg, "base_mode", 0)
            & 128  # MAV_MODE_FLAG_SAFETY_ARMED
        )
        data.update(
            connected=True,
            last_heartbeat_at=time(),
            armed=armed,
            flight_mode=mode,
            system_status=getattr(msg, "system_status", None),
        )

    elif msg_type == "GLOBAL_POSITION_INT":
        lat = getattr(msg, "lat", None)
        lon = getattr(msg, "lon", None)
        alt = getattr(msg, "alt", None)
        rel = getattr(msg, "relative_alt", None)
        hdg = getattr(msg, "hdg", None)

        data.update(
            latitude=(lat / 1e7) if lat is not None else None,
            longitude=(lon / 1e7) if lon is not None else None,
            altitude_msl_m=(alt / 1000.0) if alt is not None else None,
            relative_altitude_m=(rel / 1000.0) if rel is not None else None,
            heading_deg=(hdg / 100.0) if hdg not in (None, 65535) else None,
        )

    elif msg_type == "VFR_HUD":
        data.update(
            airspeed_m_s=getattr(msg, "airspeed", None),
            groundspeed_m_s=getattr(msg, "groundspeed", None),
            climb_m_s=getattr(msg, "climb", None),
            heading_deg=float(getattr(msg, "heading", 0)),
        )

    elif msg_type == "ATTITUDE":
        data.update(
            roll_deg=radians_to_degrees(getattr(msg, "roll", None)),
            pitch_deg=radians_to_degrees(getattr(msg, "pitch", None)),
            yaw_deg=radians_to_degrees(getattr(msg, "yaw", None)),
        )

    elif msg_type == "GPS_RAW_INT":
        eph = getattr(msg, "eph", None)
        data.update(
            gps_fix_type=getattr(msg, "fix_type", None),
            gps_satellites=getattr(msg, "satellites_visible", None),
            gps_hdop=(eph / 100.0) if eph not in (None, 65535) else None,
        )

    elif msg_type == "SYS_STATUS":
        voltage = getattr(msg, "voltage_battery", None)
        current = getattr(msg, "current_battery", None)
        remaining = getattr(msg, "battery_remaining", None)
        data.update(
            battery_voltage_v=(voltage / 1000.0) if voltage not in (None, 65535) else None,
            battery_current_a=(current / 100.0) if current not in (None, -1) else None,
            battery_percent=remaining if remaining not in (None, -1) else None,
        )

    elif msg_type == "BATTERY_STATUS":
        remaining = getattr(msg, "battery_remaining", None)
        data.update(
            battery_percent=remaining if remaining not in (None, -1) else None,
        )

    else:
        return {}

    return data

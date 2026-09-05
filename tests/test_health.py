from skysentinel.models import Telemetry
from skysentinel.telemetry.health import evaluate_health


def test_low_battery_alert():
    t = Telemetry(connected=True, battery_percent=20)
    codes = {alert.code for alert in evaluate_health(t)}
    assert "LOW_BATTERY" in codes


def test_critical_battery_alert():
    t = Telemetry(connected=True, battery_percent=10)
    codes = {alert.code for alert in evaluate_health(t)}
    assert "CRITICAL_BATTERY" in codes


def test_good_gps_has_no_gps_alert():
    t = Telemetry(connected=True, gps_fix_type=3, gps_satellites=12)
    codes = {alert.code for alert in evaluate_health(t)}
    assert "GPS_FIX_WEAK" not in codes
    assert "GPS_SATELLITES_LOW" not in codes

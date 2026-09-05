from skysentinel.telemetry.parser import radians_to_degrees


def test_radians_to_degrees():
    value = radians_to_degrees(3.141592653589793)
    assert value == 180.0


def test_none_angle():
    assert radians_to_degrees(None) is None

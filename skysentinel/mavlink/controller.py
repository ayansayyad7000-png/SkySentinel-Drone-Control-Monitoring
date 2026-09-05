from pymavlink import mavutil

from skysentinel.config import settings


class ActuationDisabled(RuntimeError):
    pass


class DroneController:
    SAFE_MODES = {"GUIDED", "LOITER", "LAND", "RTL"}

    def __init__(self, client):
        self.client = client

    @property
    def connection(self):
        if self.client.connection is None:
            raise RuntimeError("MAVLink vehicle is not connected.")
        return self.client.connection

    def _require_actuation(self):
        if not settings.allow_actuation:
            raise ActuationDisabled(
                "Actuation is disabled. Use ALLOW_ACTUATION=true only in an approved test environment."
            )

    def _ack_or_raise(self, command: int):
        ack = self.client.wait_for_command_ack(command)
        if ack is None:
            raise TimeoutError("No COMMAND_ACK received.")
        if ack.result not in (
            mavutil.mavlink.MAV_RESULT_ACCEPTED,
            mavutil.mavlink.MAV_RESULT_IN_PROGRESS,
        ):
            raise RuntimeError(f"Autopilot rejected command with MAV_RESULT={ack.result}.")
        return int(ack.result)

    def set_mode(self, mode: str):
        self._require_actuation()
        mode = mode.upper()
        if mode not in self.SAFE_MODES:
            raise ValueError(f"Mode must be one of: {sorted(self.SAFE_MODES)}")

        mapping = self.connection.mode_mapping()
        if mode not in mapping:
            raise ValueError(f"Mode {mode} is not available on this vehicle.")

        command = mavutil.mavlink.MAV_CMD_DO_SET_MODE
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            command,
            0,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mapping[mode],
            0,
            0,
            0,
            0,
            0,
        )
        return self._ack_or_raise(command)

    def arm(self):
        self._require_actuation()
        command = mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            command,
            0,
            1,
            0,
            0,
            0,
            0,
            0,
            0,
        )
        return self._ack_or_raise(command)

    def disarm(self):
        self._require_actuation()
        command = mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            command,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        )
        return self._ack_or_raise(command)

    def land(self):
        return self.set_mode("LAND")

    def rtl(self):
        return self.set_mode("RTL")

    def takeoff(self, altitude_m: float):
        self._require_actuation()
        if altitude_m <= 0 or altitude_m > settings.max_takeoff_alt_m:
            raise ValueError(
                f"Takeoff altitude must be > 0 and <= {settings.max_takeoff_alt_m} m."
            )

        command = mavutil.mavlink.MAV_CMD_NAV_TAKEOFF
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            command,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            altitude_m,
        )
        return self._ack_or_raise(command)

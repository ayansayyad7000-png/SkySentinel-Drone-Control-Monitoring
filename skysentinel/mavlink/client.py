import logging
from time import sleep

from pymavlink import mavutil

from skysentinel.config import settings
from skysentinel.telemetry.parser import parse_mavlink_message
from skysentinel.telemetry.state import TelemetryState

logger = logging.getLogger(__name__)


class MavlinkClient:
    def __init__(self, state: TelemetryState):
        self.state = state
        self.connection = None

    def connect(self) -> None:
        logger.info("Connecting to MAVLink: %s", settings.mavlink_connection)
        self.connection = mavutil.mavlink_connection(
            settings.mavlink_connection,
            baud=settings.mavlink_baud,
            autoreconnect=True,
        )

        heartbeat = self.connection.wait_heartbeat(timeout=15)
        if heartbeat is None:
            raise TimeoutError("No MAVLink heartbeat received within 15 seconds.")

        self.state.update(
            connected=True,
            system_id=self.connection.target_system,
            component_id=self.connection.target_component,
        )

        self._request_default_message_rates()
        logger.info(
            "MAVLink connected: system=%s component=%s",
            self.connection.target_system,
            self.connection.target_component,
        )

    def _set_message_interval(self, message_id: int, hz: float) -> None:
        interval_us = int(1_000_000 / hz)
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
            0,
            message_id,
            interval_us,
            0,
            0,
            0,
            0,
            0,
        )

    def _request_default_message_rates(self) -> None:
        requests = [
            (mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 5),
            (mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE, 5),
            (mavutil.mavlink.MAVLINK_MSG_ID_VFR_HUD, 2),
            (mavutil.mavlink.MAVLINK_MSG_ID_GPS_RAW_INT, 1),
            (mavutil.mavlink.MAVLINK_MSG_ID_SYS_STATUS, 1),
        ]
        for message_id, hz in requests:
            try:
                self._set_message_interval(message_id, hz)
            except Exception as exc:
                logger.debug("Could not request message %s: %s", message_id, exc)

    def read_once(self) -> bool:
        if self.connection is None:
            return False

        msg = self.connection.recv_match(blocking=False)
        if msg is None:
            return False

        updates = parse_mavlink_message(
            msg,
            mode_resolver=lambda m: mavutil.mode_string_v10(m),
        )
        if updates:
            self.state.update(**updates)
            return True
        return False

    def wait_for_command_ack(self, command: int, timeout: float = 5.0):
        if self.connection is None:
            return None

        ack = self.connection.recv_match(
            type="COMMAND_ACK",
            blocking=True,
            timeout=timeout,
            condition=f"COMMAND_ACK.command=={command}",
        )
        return ack

    def close(self) -> None:
        if self.connection is not None:
            try:
                self.connection.close()
            except Exception:
                pass
            self.connection = None
        self.state.update(connected=False)

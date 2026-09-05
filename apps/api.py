import asyncio

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect

from skysentinel.config import settings
from skysentinel.mavlink.controller import ActuationDisabled
from skysentinel.runtime import runtime

app = FastAPI(
    title="SkySentinel Drone API",
    version="1.0.0",
    description="Real-time ArduPilot MAVLink telemetry and safety-gated control API.",
)


@app.on_event("startup")
def startup():
    runtime.start()


@app.on_event("shutdown")
def shutdown():
    runtime.stop()


@app.get("/")
def root():
    return {
        "project": "SkySentinel",
        "docs": "/docs",
        "actuation_enabled": settings.allow_actuation,
    }


@app.get("/health")
def health():
    payload = runtime.telemetry_payload()
    return {
        "api": "ok",
        "vehicle_connected": payload["telemetry"]["connected"],
        "alerts": payload["alerts"],
        "actuation_enabled": settings.allow_actuation,
    }


@app.get("/telemetry")
def telemetry():
    return runtime.telemetry_payload()


def _control_call(fn, *args, **kwargs):
    try:
        result = fn(*args, **kwargs)
        return {"accepted": True, "mav_result": result}
    except ActuationDisabled as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/control/mode/{mode}")
def set_mode(mode: str):
    return _control_call(runtime.controller.set_mode, mode)


@app.post("/control/arm")
def arm():
    return _control_call(runtime.controller.arm)


@app.post("/control/disarm")
def disarm():
    return _control_call(runtime.controller.disarm)


@app.post("/control/rtl")
def rtl():
    return _control_call(runtime.controller.rtl)


@app.post("/control/land")
def land():
    return _control_call(runtime.controller.land)


@app.post("/control/takeoff")
def takeoff(altitude_m: float = 5):
    return _control_call(runtime.controller.takeoff, altitude_m)


@app.websocket("/ws/telemetry")
async def telemetry_socket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(runtime.telemetry_payload())
            await asyncio.sleep(0.25)
    except WebSocketDisconnect:
        pass

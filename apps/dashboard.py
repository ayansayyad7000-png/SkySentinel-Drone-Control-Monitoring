import time
from collections import deque

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API_URL = st.sidebar.text_input("API URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="SkySentinel", page_icon="🚁", layout="wide")
st.title("🚁 SkySentinel — Real-Time Drone Monitoring")
st.caption("ArduPilot MAVLink telemetry dashboard")

if "history" not in st.session_state:
    st.session_state.history = deque(maxlen=120)

refresh_ms = st.sidebar.slider("Refresh interval (ms)", 250, 3000, 750, 250)
auto_refresh = st.sidebar.toggle("Auto refresh", value=True)

try:
    response = requests.get(f"{API_URL}/telemetry", timeout=1.5)
    response.raise_for_status()
    payload = response.json()
    t = payload["telemetry"]
    alerts = payload["alerts"]

    st.session_state.history.append(
        {
            "time": pd.Timestamp.now(),
            "altitude_m": t.get("relative_altitude_m"),
            "groundspeed_m_s": t.get("groundspeed_m_s"),
            "battery_percent": t.get("battery_percent"),
        }
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Connection", "ONLINE" if t.get("connected") else "OFFLINE")
    c2.metric("Flight Mode", t.get("flight_mode") or "UNKNOWN")
    c3.metric("Armed", "YES" if t.get("armed") else "NO")
    c4.metric("Altitude", f"{t.get('relative_altitude_m') or 0:.1f} m")
    c5.metric("Battery", f"{t.get('battery_percent') if t.get('battery_percent') is not None else '--'} %")

    st.subheader("📍 Navigation")
    n1, n2, n3, n4 = st.columns(4)
    n1.metric("Latitude", f"{t.get('latitude'):.6f}" if t.get("latitude") is not None else "--")
    n2.metric("Longitude", f"{t.get('longitude'):.6f}" if t.get("longitude") is not None else "--")
    n3.metric("Heading", f"{t.get('heading_deg'):.1f}°" if t.get("heading_deg") is not None else "--")
    n4.metric("Satellites", t.get("gps_satellites") if t.get("gps_satellites") is not None else "--")

    st.subheader("📐 Attitude")
    a1, a2, a3 = st.columns(3)
    a1.metric("Roll", f"{t.get('roll_deg'):.1f}°" if t.get("roll_deg") is not None else "--")
    a2.metric("Pitch", f"{t.get('pitch_deg'):.1f}°" if t.get("pitch_deg") is not None else "--")
    a3.metric("Yaw", f"{t.get('yaw_deg'):.1f}°" if t.get("yaw_deg") is not None else "--")

    st.subheader("📊 Flight Trends")
    df = pd.DataFrame(st.session_state.history)
    if not df.empty:
        left, right = st.columns(2)
        with left:
            st.plotly_chart(
                px.line(df, x="time", y="altitude_m", title="Relative Altitude"),
                use_container_width=True,
            )
        with right:
            st.plotly_chart(
                px.line(df, x="time", y="battery_percent", title="Battery %"),
                use_container_width=True,
            )

    st.subheader("🩺 Health")
    if not alerts:
        st.success("No active health warnings.")
    else:
        for alert in alerts:
            text = f"{alert['code']}: {alert['message']}"
            if alert["level"] == "critical":
                st.error(text)
            else:
                st.warning(text)

except Exception as exc:
    st.error(f"Could not reach SkySentinel API: {exc}")

if auto_refresh:
    time.sleep(refresh_ms / 1000)
    st.rerun()

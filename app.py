import streamlit as st
import datetime
import math
import requests

st.set_page_config(
    page_title="ShadowCompile — Solar Build Synchronizer",
    page_icon="☀️",
    layout="centered"
)

st.title("☀️ ShadowCompile")
st.caption("Synchronize your code compilation breaks with solar mechanics. Powered by Open-Source AI.")

# --- Solar Calculation Engine (Standard Astronomy Formulas) ---
def compute_solar_metrics(lat: float, lon: float, dt: datetime.datetime):
    """
    Computes solar elevation angle and estimated shadow multiplier
    without requiring third-party celestial dependencies.
    """
    day_of_year = dt.timetuple().tm_yday
    # Solar declination approximation (in radians)
    declination = math.radians(23.45 * math.sin(math.radians((360 / 365) * (day_of_year - 81))))
    
    # Equation of time & solar time adjustment
    b = math.radians((360 / 365) * (day_of_year - 81))
    eot = 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)
    time_offset = eot + 4 * lon
    solar_time_minutes = dt.hour * 60 + dt.minute + dt.second / 60 + time_offset
    hour_angle = math.radians((solar_time_minutes / 4) - 180)
    
    lat_rad = math.radians(lat)
    
    # Solar elevation angle
    sin_elevation = (
        math.sin(lat_rad) * math.sin(declination) +
        math.cos(lat_rad) * math.cos(declination) * math.cos(hour_angle)
    )
    elevation_rad = math.asin(max(-1.0, min(1.0, sin_elevation)))
    elevation_deg = math.degrees(elevation_rad)
    
    # Shadow ratio = 1 / tan(elevation)
    if elevation_deg > 2.0:
        shadow_ratio = 1.0 / math.tan(elevation_rad)
        sun_state = "Direct Daylight"
    elif elevation_deg > -6.0:
        shadow_ratio = None
        sun_state = "Civil Twilight / Low Horizon"
    else:
        shadow_ratio = None
        sun_state = "Night / Nocturnal"
        
    return elevation_deg, shadow_ratio, sun_state

# --- App State Management ---
if "active_break" not in st.session_state:
    st.session_state.active_break = False
if "break_payload" not in st.session_state:
    st.session_state.break_payload = None

# --- UI Mode 1: Configuration & Build Trigger ---
if not st.session_state.active_break:
    st.markdown("### ⚙️ Build Context")
    
    col1, col2 = st.columns(2)
    with col1:
        task_type = st.selectbox(
            "What process are you running?",
            [
                "C++ / Rust Cargo Clean Build",
                "Machine Learning Training Epochs",
                "Full Test Suite / CI Execution",
                "Database Migration & Seeding",
                "Docker Compose Image Rebuild"
            ]
        )
    with col2:
        break_duration = st.slider("Target Break Duration (Minutes)", 5, 30, 10, step=5)

    st.markdown("### 📍 Location Coordinates")
    col_lat, col_lon = st.columns(2)
    with col_lat:
        user_lat = st.number_input("Latitude", value=18.5204, format="%.4f", help="Defaults to Pune, India")
    with col_lon:
        user_lon = st.number_input("Longitude", value=73.8567, format="%.4f")

    now = datetime.datetime.now()
    elevation, ratio, state = compute_solar_metrics(user_lat, user_lon, now)

    # Real-time Solar Telemetry Cards
    st.markdown("#### 🛰️ Live Solar Telemetry")
    m1, m2, m3 = st.columns(3)
    m1.metric("Sun Status", state)
    m2.metric("Solar Elevation", f"{elevation:.1f}°")
    m3.metric("Shadow Multiplier", f"{ratio:.2f}x" if ratio else "Diffuse")

    # Generate Button
    if st.button("🚀 Trigger Build & Generate Solar Challenge", type="primary", use_container_width=True):
        with st.spinner("Synthesizing solar mission with open-weight Gemma model..."):
            
            prompt = (
                f"You are a developer wellness engineer. The programmer triggered: {task_type}. "
                f"Break length: {break_duration} minutes. Current solar elevation: {elevation:.1f} degrees ({state}). "
                f"Shadow length ratio: {f'{ratio:.2f}x height' if ratio else 'diffuse light'}. "
                "Generate 2 brief real-world outdoor tasks: one based on verifying shadow orientation/sunlight angle, "
                "and one tactile observation (e.g., foliage, wind direction, ambient heat). Keep it punchy."
            )
            
            API_URL = "https://api-inference.huggingface.co/models/google/gemma-2-2b-it"
            
            try:
                response = requests.post(
                    API_URL,
                    json={"inputs": prompt, "parameters": {"max_new_tokens": 200}},
                    timeout=10
                )
                if response.status_code == 200:
                    raw = response.json()[0].get("generated_text", "")
                    ai_task = raw.replace(prompt, "").strip()
                else:
                    ai_task = None
            except Exception:
                ai_task = None

            # Deterministic fallback guaranteeing zero downtime
            if not ai_task or len(ai_task) < 15:
                if ratio:
                    shadow_note = f"Your shadow should be roughly {ratio:.1f}x your height. Notice which wall or path it points toward."
                else:
                    shadow_note = "Notice the ambient sky gradient and whether low-angle diffuse light creates soft silhouettes."
                    
                ai_task = (
                    f"**1. Solar Alignment Task:** Step outside into open air. {shadow_note}\n\n"
                    f"**2. Sensory Recalibration:** Stand away from all monitors. Close your eyes for 45 seconds and gauge the ambient outdoor air temperature against your skin."
                )

            st.session_state.break_payload = {
                "task": task_type,
                "duration": break_duration,
                "elevation": elevation,
                "ratio": ratio,
                "challenge": ai_task
            }
            st.session_state.active_break = True
            st.rerun()

# --- UI Mode 2: The "Touch Grass" Screen Lockout ---
else:
    payload = st.session_state.break_payload
    
    st.error("🛑 SCREEN LOCKOUT ACTIVE — STEP AWAY FROM THE TERMINAL")
    st.info(f"⏳ **Build in progress:** {payload['task']} | **Allocated Outdoor Time:** {payload['duration']} mins")
    
    st.markdown("---")
    st.markdown("### 🌲 Your Outdoor Solar Mission")
    st.markdown(payload["challenge"])
    
    if payload["ratio"]:
        st.caption(f"📐 Physics check: A 1.8m person will currently cast an approximately {1.8 * payload['ratio']:.2f}m shadow.")
    
    st.markdown("---")
    st.warning("⚠️ Do not stare at code compilation logs. Close your laptop lid or lock your workstation right now.")
    
    if st.button("✅ Build Complete — I Verified My Shadow Outside", type="primary", use_container_width=True):
        st.session_state.active_break = False
        st.session_state.break_payload = None
        st.balloons()
        st.success("🎉 Brain refreshed, circadian clock synced, compilation complete!")
        st.rerun()

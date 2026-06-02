import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# --- CONFIGURATION & PAGE SETUP ---
st.set_page_config(page_title="Advanced ODD Campaign Engine", page_icon="⚙️", layout="wide")

# --- SYSTEMS ENGINEERING REQUIREMENTS (V&V TARGETS) ---
SYS_REQS = {
    "radar_min_conf": 0.80,    # RF must penetrate weather
    "lidar_min_conf": 0.30,    # Optical scattering floor
    "camera_min_conf": 0.40,   # Visual object classification floor
    "min_traction_coeff": 0.60,# Minimum grip before hydroplaning/sliding occurs
    "max_critical_failures": 5 # Strict pass/fail gate for regression testing
}

# --- DATA GENERATION ENGINE ---
@st.cache_data
def fetch_advanced_weather():
    """Generates a highly dynamic 30-day ODD logistics forecast."""
    np.random.seed(105)
    dates = [datetime.now() + timedelta(days=i) for i in range(30)]
    temps = np.random.normal(5, 12, 30)
    
    conditions = []
    surfaces = []
    visibility = []
    
    for t in temps:
        chance = np.random.uniform(0, 100)
        if t < 0 and chance > 70:
            conditions.append("Heavy Snow")
            surfaces.append("Ice/Slush")
            visibility.append(np.random.uniform(100, 400))
        elif t > 0 and chance > 85:
            conditions.append("Hail / Torrential")
            surfaces.append("Flooded")
            visibility.append(np.random.uniform(50, 300))
        elif t > 0 and chance > 50:
            conditions.append("Rain")
            surfaces.append("Wet/Slick")
            visibility.append(np.random.uniform(800, 2000))
        elif chance > 30 and t < 10:
            conditions.append("Dense Fog")
            surfaces.append("Damp")
            visibility.append(np.random.uniform(10, 100))
        else:
            conditions.append("Clear")
            surfaces.append("Dry")
            visibility.append(10000)

    return pd.DataFrame({
        "Date": [d.strftime("%Y-%m-%d") for d in dates],
        "Temp (C)": temps.round(1),
        "Atmospheric State": conditions,
        "Road Surface": surfaces,
        "Visibility (m)": [int(v) for v in visibility]
    })

@st.cache_data
def run_dynamic_validation(platform, frames, weather, surface, speed_mph):
    """Correlates weather, surface conditions, and vehicle kinematics to sensor performance."""
    np.random.seed(42 if platform == "Production Release" else 99)
    time_ms = np.arange(frames) * 10
    
    # 1. Base Sensor Degradation profiles
    mod_radar, mod_lidar, mod_camera = 1.0, 1.0, 1.0
    
    if weather == "Heavy Snow":
        mod_lidar, mod_camera = 0.4, 0.3
    elif weather == "Hail / Torrential":
        mod_radar, mod_lidar, mod_camera = 0.85, 0.3, 0.2
    elif weather == "Dense Fog":
        mod_lidar, mod_camera = 0.6, 0.1
        
    # 2. Road Surface & Kinematics (Traction Engine)
    base_traction = 0.95
    if surface == "Ice/Slush":
        base_traction = 0.40
    elif surface == "Flooded":
        base_traction = 0.80 - (speed_mph / 100)
    elif surface == "Wet/Slick":
        base_traction = 0.75 - (speed_mph / 150)
        
    # Generate Time-Series Data
    radar = np.clip((0.95 * mod_radar) + np.random.normal(0, 0.05, frames), 0.1, 1.0)
    lidar = np.clip((0.90 * mod_lidar) + np.random.normal(0, 0.10, frames), 0.01, 1.0)
    camera = np.clip((0.90 * mod_camera) + np.random.normal(0, 0.15, frames), 0.01, 1.0)
    traction = np.clip(base_traction + np.random.normal(0, 0.08, frames), 0.1, 1.0)
    
    # Inject Hardware Instability for Prototypes
    if platform == "Hardware Prototype (v2.4)":
        radar[np.random.choice(frames, int(frames*0.02), replace=False)] -= 0.30
        
    # Inject Splash-back occlusion events for camera on wet roads
    if surface in ["Flooded", "Wet/Slick"] and speed_mph > 30:
        splash_frames = np.random.choice(frames, int(frames*0.05), replace=False)
        camera[splash_frames] = np.random.uniform(0.01, 0.15)

    return pd.DataFrame({
        "Timestamp_ms": time_ms,
        "Radar_Conf": radar,
        "LiDAR_Conf": lidar,
        "Camera_Conf": camera,
        "Traction_Coeff": traction,
        "Vehicle_Speed": np.random.normal(speed_mph, 2, frames)
    })

# --- UI ARCHITECTURE ---
st.title("Advanced ODD Campaign & Dynamics Engine")
st.markdown("Unified platform correlating environmental logistics, multi-modal sensor V&V, and vehicle kinematics.")

tab_logistics, tab_validation, tab_reporting = st.tabs([
    "📍 Facility Logistics Matrix", 
    "⚙️ Dynamic Simulation Runner", 
    "📊 Executive Analytics"
])

# ==========================================
# TAB 1: LOGISTICS
# ==========================================
with tab_logistics:
    st.header("External Test Facility: Keweenaw Research Center (KRC)")
    c1, c2, c3 = st.columns(3)
    c1.metric(
        "Target ODD", 
        "Multi-Condition Stress", 
        help="The defined operational boundaries requiring validation, specifically extreme weather and degraded surface friction."
    )
    c2.metric(
        "Facility Availability", 
        "Confirmed (30-Day Window)", 
        help="Contractual operational window for proving ground access. High utilization required to minimize cost-burn."
    )
    c3.metric(
        "Hardware Platform Readiness", 
        "In Transit", 
        delta="-2 Days", 
        help="Logistical status of physical sensor suites. Delays require schedule compression."
    )
    
    st.divider()
    st.subheader("30-Day Tactical Environmental Forecast", help="Long-range meteorological projection for deployment scheduling.")
    weather_df = fetch_advanced_weather()
    
    # Visual Calendar / Temperature Plot
    st.bar_chart(weather_df.set_index("Date")["Temp (C)"], height=200)
    
    # High Contrast Styling Logic
    def highlight_odd(val):
        if val in ["Heavy Snow", "Hail / Torrential", "Ice/Slush", "Flooded"]:
            return 'background-color: #8b0000; color: #ffffff;' # Dark Red
        elif val in ["Rain", "Dense Fog", "Wet/Slick"]:
            return 'background-color: #b8860b; color: #ffffff;' # Dark Goldenrod
        return ''
    
    st.dataframe(weather_df.style.map(highlight_odd, subset=['Atmospheric State', 'Road Surface']), use_container_width=True)
    st.caption("Red formatting denotes severe edge case testing parameters. Orange denotes moderate degradation. Thermal chart displays daily mean temperature.")

# ==========================================
# TAB 2: V&V SIMULATION RUNNER
# ==========================================
with tab_validation:
    st.header("Dynamic Sensor & Kinematics Simulator")
    
    c_env, c_veh, c_sys = st.columns(3)
    with c_env:
        st.subheader("Environmental Parameters")
        sim_weather = st.selectbox(
            "Atmospheric State", 
            ["Clear", "Rain", "Dense Fog", "Heavy Snow", "Hail / Torrential"],
            help="Modulates optical scattering (LiDAR) and multi-path RF attenuation (Radar)."
        )
        sim_surface = st.selectbox(
            "Road Surface State", 
            ["Dry", "Damp", "Wet/Slick", "Flooded", "Ice/Slush"],
            help="Modulates the baseline friction coefficient for the chassis traction model."
        )
    with c_veh:
        st.subheader("Vehicle Kinematics")
        sim_speed = st.slider(
            "Target Speed (mph)", 
            10, 85, 45, 5, 
            help="Longitudinal velocity. Higher speeds degrade the traction coefficient exponentially on compromised surfaces."
        )
        test_frames = st.slider(
            "Evaluation Window (Frames)", 
            500, 5000, 2000, 500,
            help="Total time-series array size. Processed at 100Hz (2000 frames = 20 seconds)."
        )
    with c_sys:
        st.subheader("Systems Architecture")
        platform = st.selectbox(
            "Hardware Platform", 
            ["Production Release", "Hardware Prototype (v2.4)"],
            help="'Production' utilizes stable nominal baselines. 'Prototype' injects unverified hardware instability and stochastic dropouts."
        )
        st.info("Execution engine correlates physical mathematics between surface tension, velocity, and optical scattering.")
        run_test = st.button("▶ Execute Dynamic V&V Pipeline", type="primary", use_container_width=True)

    if run_test:
        with st.spinner('Calculating multi-modal dynamics...'):
            test_data = run_dynamic_validation(platform, test_frames, sim_weather, sim_surface, sim_speed)
            
            # Diagnostic Counters
            fails_r = len(test_data[test_data["Radar_Conf"] < SYS_REQS['radar_min_conf']])
            fails_c = len(test_data[test_data["Camera_Conf"] < SYS_REQS['camera_min_conf']])
            fails_t = len(test_data[test_data["Traction_Coeff"] < SYS_REQS['min_traction_coeff']])
            
            st.session_state.update({
                'td': test_data, 'plat': platform, 'env': f"{sim_weather} / {sim_surface}",
                'fr': fails_r, 'fc': fails_c, 'ft': fails_t
            })
            st.success("Simulation Complete. Analytics cached to Executive Report.")

# ==========================================
# TAB 3: EXECUTIVE REPORTING
# ==========================================
with tab_reporting:
    st.header("Technical Qualification Report")
    
    if 'td' not in st.session_state:
        st.warning("Awaiting data. Please execute a simulation in the Runner tab.")
    else:
        df = st.session_state['td']
        total_fails = st.session_state['fr'] + st.session_state['fc'] + st.session_state['ft']
        
        if total_fails > SYS_REQS['max_critical_failures']:
            status, color = "SYSTEM FAILED QUALIFICATION", "red"
        else:
            status, color = "SYSTEM PASSED QUALIFICATION", "green"
            
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Platform Tested", st.session_state['plat'], help="The targeted hardware/software build under evaluation.")
        m2.metric("ODD Environment", st.session_state['env'], help="The simulated atmospheric and surface conditions.")
        m3.metric("Critical System Failures", total_fails, help="Aggregate count of instances where any sensor or traction metric fell below safety thresholds.")
        m4.markdown(f"### Status: :{color}[{status}]")
        
        st.divider()
        
        # CHART 1: SENSORS
        st.subheader("Tri-Sensor Attenuation Analysis", help="Evaluates RF and Optical penetration against atmospheric conditions. Dotted line represents the minimum safety threshold for primary RF tracking.")
        fig_s, ax_s = plt.subplots(figsize=(12, 3.5))
        ax_s.plot(df["Timestamp_ms"], df["Radar_Conf"], color="#2c3e50", alpha=0.9, label="Radar (RF)")
        ax_s.plot(df["Timestamp_ms"], df["Camera_Conf"], color="#8e44ad", alpha=0.6, label="Camera (Optical)")
        ax_s.plot(df["Timestamp_ms"], df["LiDAR_Conf"], color="#3498db", alpha=0.4, label="LiDAR (Laser)")
        ax_s.axhline(y=SYS_REQS['radar_min_conf'], color="#e74c3c", linestyle="--", label="Radar Safety Floor")
        ax_s.set_ylabel("Confidence Matrix (0.0-1.0)")
        ax_s.legend(loc="lower right")
        st.pyplot(fig_s)
        
        # CHART 2: KINEMATICS
        st.subheader("Vehicle Dynamics & Traction Profile", help="Evaluates physical chassis stability based on velocity and road surface friction. Dotted line represents the hydroplane or slip-angle threshold.")
        fig_t, ax_t = plt.subplots(figsize=(12, 3.5))
        ax_t.plot(df["Timestamp_ms"], df["Traction_Coeff"], color="#27ae60", label="Traction Coefficient")
        ax_t.axhline(y=SYS_REQS['min_traction_coeff'], color="#e74c3c", linestyle="--", label="Hydroplane / Slip Threshold")
        
        # Highlight slip events
        if st.session_state['ft'] > 0:
            slips = df[df["Traction_Coeff"] < SYS_REQS['min_traction_coeff']]
            ax_t.scatter(slips["Timestamp_ms"], slips["Traction_Coeff"], color="red", zorder=5, label="Loss of Control Event")
            
        ax_t.set_xlabel("Test Duration (ms)")
        ax_t.set_ylabel("Grip Coefficient")
        ax_t.legend(loc="lower right")
        st.pyplot(fig_t)

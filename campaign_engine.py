import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# --- CONFIGURATION & PAGE SETUP ---
st.set_page_config(page_title="ODD Campaign Engine", page_icon="⚙️", layout="wide")

# --- SYSTEMS ENGINEERING REQUIREMENTS (V&V TARGETS) ---
# Hardcoded system-level requirements for automated verification
SYS_REQS = {
    "radar_snow_min_conf": 0.80,  # Radar must maintain 80% confidence in snow
    "lidar_snow_min_conf": 0.30,  # LiDAR allowed to degrade, but floor is 30%
    "max_allowable_latency_ms": 50,
    "max_critical_failures": 5    # System fails validation if > 5 edge cases occur
}

# --- DATA GENERATION (Simulating Field Test Operations) ---
@st.cache_data
def fetch_weather_window():
    """Simulates a 14-day weather forecast at an external testing facility."""
    np.random.seed(101)
    dates = [datetime.now() + timedelta(days=i) for i in range(14)]
    temps = np.random.normal(-5, 8, 14) # Cold weather target
    precip = np.random.uniform(0, 100, 14) # Precipitation chance
    
    return pd.DataFrame({
        "Date": [d.strftime("%Y-%m-%d") for d in dates],
        "Temp (C)": temps.round(1),
        "Precip Chance (%)": precip.round(1),
        "ODD Condition": ["Heavy Snow" if p > 70 and t < 0 else "Clear/Cold" for p, t in zip(precip, temps)]
    })

@st.cache_data
def run_automated_validation(hardware_type, duration_frames=2000):
    """Simulates automated V&V data acquisition for Radar/LiDAR prototypes."""
    np.random.seed(42 if hardware_type == "Production Release" else 99)
    
    time_ms = np.arange(duration_frames) * 10
    
    # Radar is generally robust, but the prototype has random attenuation drops
    base_radar = 0.95
    radar_noise = np.random.normal(0, 0.05, duration_frames)
    if hardware_type == "Hardware Prototype (v2.4)":
        radar_noise[np.random.choice(duration_frames, 20, replace=False)] -= 0.30 # Induce severe drops
    
    # LiDAR degrades heavily in snow
    base_lidar = 0.60
    lidar_noise = np.random.normal(0, 0.15, duration_frames)
    
    df = pd.DataFrame({
        "Timestamp (ms)": time_ms,
        "Radar_Confidence": np.clip(base_radar + radar_noise, 0.1, 1.0),
        "LiDAR_Confidence": np.clip(base_lidar + lidar_noise, 0.05, 1.0),
        "Compute_Latency_ms": np.random.normal(30, 10, duration_frames)
    })
    return df

# --- UI ARCHITECTURE ---
st.title("Winter ODD Test Campaign & V&V Engine")
st.markdown("Unified platform for external facility logistics and automated sensor verification.")

# Create main tabs for the application
tab_logistics, tab_validation, tab_reporting = st.tabs([
    "📍 Facility Logistics & TPM", 
    "⚙️ Automated V&V Runner", 
    "📊 Executive Technical Report"
])

# ==========================================
# TAB 1: LOGISTICS & CAMPAIGN MANAGEMENT
# ==========================================
with tab_logistics:
    st.header("External Test Facility: Keweenaw Research Center (KRC)")
    st.markdown("Tracking seasonal windows and resource readiness for winter deployment.")
    
    c1, c2, c3 = st.columns(3)
    c1.metric(
        "Target Operational Design Domain (ODD)", 
        "Heavy Snow / Sub-Zero",
        help="**ELI5:** The specific weather we need to test the car in to prove it is safe.\n\n**Technical:** The formally defined environmental constraints (Temperature < 0°C, Precipitation > 70%) under which the autonomous system is designed to operate safely."
    )
    c2.metric(
        "Facility Availability", 
        "Confirmed (Nov 15 - Dec 20)",
        help="**ELI5:** The dates we rented the test track.\n\n**Technical:** Contractual window for exclusive access to the KRC winter proving grounds. Cost-burn rate mandates high-efficiency testing during this period."
    )
    c3.metric(
        "Hardware Platform Readiness", 
        "In Transit", 
        delta="-2 Days (Delayed)", 
        delta_color="inverse",
        help="**ELI5:** The new sensors are on a truck, but they are late.\n\n**Technical:** Logistics tracker for Prototype v2.4 LiDAR/Radar suites. Supply chain friction requires proactive schedule compression to hit milestones."
    )
    
    st.subheader("14-Day Tactical Weather Window", help="Forecast model to align engineering team deployment with optimal ODD conditions.")
    weather_df = fetch_weather_window()
    
    # Highlight days that meet the heavy snow requirement
    def highlight_snow(val):
        color = '#27ae60' if val == 'Heavy Snow' else ''
        return f'background-color: {color}; color: white' if val == 'Heavy Snow' else ''
    
    st.dataframe(weather_df.style.map(highlight_snow, subset=['ODD Condition']), use_container_width=True)
    
    # Go/No-Go Logic
    target_days = len(weather_df[weather_df["ODD Condition"] == "Heavy Snow"])
    if target_days >= 3:
        st.success(f"Logistics Clear: {target_days} prime ODD days identified. Teams are GREEN for deployment.")
    else:
        st.warning(f"Logistics Risk: Only {target_days} ODD days found. Consider extending facility contract.")

# ==========================================
# TAB 2: AUTOMATED V&V RUNNER
# ==========================================
with tab_validation:
    st.header("Automated Sensor Verification Pipeline")
    st.markdown("Execute automated regression tests against System Level Requirements.")
    
    col_input, col_reqs = st.columns([1, 1])
    with col_input:
        platform = st.selectbox(
            "Select Target Hardware/Software Platform:", 
            ["Production Release", "Hardware Prototype (v2.4)"],
            help="**ELI5:** Are we testing the software currently in customer cars, or the secret new hardware we just built?\n\n**Technical:** Selects the data generation seed and expected noise floor. 'Production' represents nominal baselines. 'Prototype' injects unverified hardware instability."
        )
        test_frames = st.slider(
            "Evaluation Window (Total Frames)", 
            500, 5000, 2000, 500,
            help="**ELI5:** How long the car drives during the test. 2000 frames is 20 seconds.\n\n**Technical:** The total array size generated for the time-series simulation. Processed at 100Hz (10ms per frame)."
        )
        run_test = st.button("▶ Execute Automated Test Pipeline", type="primary")
        
    with col_reqs:
        with st.expander("View Systems Engineering Coverage Requirements", expanded=True):
            st.info(
                f"**System Level Pass/Fail Criteria:**\n\n"
                f"1. **Radar Performance:** Target confidence must remain **>{SYS_REQS['radar_snow_min_conf']*100}%** in heavy snow. (RF waves should cut through precipitation).\n"
                f"2. **LiDAR Performance:** Target confidence floor is **>{SYS_REQS['lidar_snow_min_conf']*100}%**. (Optical scattering is expected, but complete blindness is a failure).\n"
                f"3. **Anomaly Tolerance:** Maximum of **{SYS_REQS['max_critical_failures']}** edge case failures permitted per validation run."
            )

    if run_test:
        with st.spinner('Acquiring field data and compiling pipeline...'):
            test_data = run_automated_validation(platform, test_frames)
            
            # V&V Math Engine
            radar_fails = test_data[test_data["Radar_Confidence"] < SYS_REQS['radar_snow_min_conf']]
            lidar_fails = test_data[test_data["LiDAR_Confidence"] < SYS_REQS['lidar_snow_min_conf']]
            
            # Save to session state for the reporting tab
            st.session_state['test_data'] = test_data
            st.session_state['platform'] = platform
            st.session_state['radar_fails'] = len(radar_fails)
            
            st.success("Test Complete. Data cached for executive reporting.")
            
            # Debugging Output
            st.subheader("Actionable Debug Data (Root Cause Identification)")
            if len(radar_fails) > 0:
                st.error(
                    f"⚠️ {len(radar_fails)} Radar Attenuation Events Detected.\n\n"
                    "**Technical Root Cause:** The array below identifies the exact milliseconds where RF energy dropped below the 0.80 safety threshold, indicating potential water intrusion on the radome or a multi-path calculation error."
                )
                st.dataframe(radar_fails.head(5), use_container_width=True)
            else:
                st.success("Zero Radar verification failures. Hardware is nominal.")

# ==========================================
# TAB 3: EXECUTIVE REPORTING
# ==========================================
with tab_reporting:
    st.header("Technical Campaign Report")
    
    if 'test_data' not in st.session_state:
        st.warning("No data found. Please execute a test in the V&V Runner tab first.")
    else:
        df = st.session_state['test_data']
        r_fails = st.session_state['radar_fails']
        plat = st.session_state['platform']
        
        # Calculate Pass/Fail status
        if r_fails > SYS_REQS['max_critical_failures']:
            final_status, status_color = "FAILED QUALIFICATION", "red"
        else:
            final_status, status_color = "PASSED QUALIFICATION", "green"
            
        c1, c2, c3 = st.columns(3)
        c1.metric("Platform Tested", plat)
        c2.metric(
            "Radar Verification Drops", 
            r_fails,
            help=f"Total frames where Radar confidence fell below {SYS_REQS['radar_snow_min_conf']}."
        )
        c3.markdown(f"### V&V Status: :{status_color}[{final_status}]")
        
        st.divider()
        st.subheader(
            "Sensor Attenuation Analysis (Time-Series)",
            help="**How to read this chart:** The X-axis is time. The Y-axis is how confident the autonomous brain is that it sees a target. The dotted red line is the absolute minimum safety standard. Any dots that appear below the red line represent critical safety failures."
        )
        
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(df["Timestamp (ms)"], df["Radar_Confidence"], color="#2c3e50", alpha=0.9, label="Radar (Main RF Sensor)")
        ax.plot(df["Timestamp (ms)"], df["LiDAR_Confidence"], color="#3498db", alpha=0.4, label="LiDAR (Secondary Optical Sensor)")
        ax.axhline(y=SYS_REQS['radar_snow_min_conf'], color="#e74c3c", linestyle="--", label="Radar Safety Threshold (0.80)")
        
        # Highlight anomalies natively in the plot
        if r_fails > 0:
            anomalies = df[df["Radar_Confidence"] < SYS_REQS['radar_snow_min_conf']]
            ax.scatter(anomalies["Timestamp (ms)"], anomalies["Radar_Confidence"], color="red", zorder=5, label="Critical Failure Points")
            
        ax.set_title(f"Multi-Sensor Performance under Simulated Snow ({plat})")
        ax.set_xlabel("Test Duration (ms)")
        ax.set_ylabel("Confidence Score (0.0 to 1.0)")
        ax.legend(loc="lower right")
        st.pyplot(fig)
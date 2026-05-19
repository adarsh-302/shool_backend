"""
Streamlit Dashboard - Real-time sensor data visualization
"""
import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go

from app_compat import cutoff_timestamp, rerun_streamlit

DB_FILE = "sensor_data.db"

# Page config
st.set_page_config(
    page_title="Sensor Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Sensor Data Dashboard")

# Database query function
def get_data(hours=24):
    query = '''
        SELECT timestamp, device_id, sensor_name, value, unit, date_field, time_field
        FROM readings 
        WHERE timestamp > ?
        ORDER BY timestamp DESC
    '''
    try:
        with sqlite3.connect(DB_FILE) as conn:
            df = pd.read_sql_query(query, conn, params=(cutoff_timestamp(hours),))
    except (sqlite3.OperationalError, pd.errors.DatabaseError):
        return pd.DataFrame(columns=["timestamp", "device_id", "sensor_name", "value", "unit", "date_field", "time_field"])
    
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    return df

def get_devices():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT device_id FROM readings ORDER BY device_id')
            devices = [row[0] for row in cursor.fetchall()]
        return devices
    except sqlite3.OperationalError:
        return []

def get_sensors_for_device(device_id):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT sensor_name FROM readings WHERE device_id = ? ORDER BY sensor_name', (device_id,))
            sensors = [row[0] for row in cursor.fetchall()]
        return sensors
    except sqlite3.OperationalError:
        return []

def get_stats(device_id, sensor_name, hours=24):
    query = '''
        SELECT AVG(value) as avg_val, MIN(value) as min_val, MAX(value) as max_val, COUNT(*) as count
        FROM readings
        WHERE device_id = ? AND sensor_name = ? AND timestamp > ?
    '''
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (device_id, sensor_name, cutoff_timestamp(hours)))
            result = cursor.fetchone()
    except sqlite3.OperationalError:
        result = None
    
    if result and result[0] is not None:
        return {
            'avg': result[0],
            'min': result[1],
            'max': result[2],
            'count': result[3]
        }
    return {'avg': None, 'min': None, 'max': None, 'count': 0}

# Sidebar controls
st.sidebar.header("⚙️ Filters")
hours = st.sidebar.slider("Show data from last (hours):", 1, 168, 24)
refresh_interval = st.sidebar.slider("Auto-refresh interval (seconds):", 5, 60, 10)

# Get data
df = get_data(hours)
devices = get_devices()

if df.empty:
    st.warning("⚠️ No data yet. Make sure MQTT consumer is running and publishing data.")
    st.info(f"Looking for data in: {DB_FILE}")
else:
    # Device selector
    selected_device = st.sidebar.selectbox("Select Device:", devices if devices else ["No devices"])
    
    if selected_device and selected_device != "No devices":
        # Filter data for selected device
        device_df = df[df['device_id'] == selected_device]
        sensors = get_sensors_for_device(selected_device)
        
        st.subheader(f"📊 Device: {selected_device}")
        
        # Summary metrics
        st.subheader("📈 Summary Statistics")
        cols = st.columns(min(len(sensors), 5))
        
        for idx, sensor in enumerate(sensors):
            stats = get_stats(selected_device, sensor, hours)
            col_idx = idx % 5
            with cols[col_idx]:
                if stats['avg'] is not None:
                    st.metric(
                        label=sensor,
                        value=f"{stats['avg']:.2f}",
                        delta=f"Min: {stats['min']:.2f} | Max: {stats['max']:.2f}"
                    )
                else:
                    st.metric(label=sensor, value="No data")
        
        # Charts for each sensor
        st.subheader("📉 Sensor Readings Over Time")
        
        for sensor in sensors:
            sensor_data = device_df[device_df['sensor_name'] == sensor].sort_values('timestamp')
            
            if len(sensor_data) > 0:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Plotly interactive chart
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=sensor_data['timestamp'],
                        y=sensor_data['value'],
                        mode='lines+markers',
                        name=sensor,
                        line=dict(color='#1f77b4', width=2),
                        marker=dict(size=6)
                    ))
                    
                    unit = sensor_data['unit'].iloc[0] if not sensor_data['unit'].isna().all() else ""
                    fig.update_layout(
                        title=f"{sensor} {f'({unit})' if unit else ''}",
                        xaxis_title="Time",
                        yaxis_title="Value",
                        hovermode='x unified',
                        height=400,
                        template='plotly_white'
                    )
                    st.plotly_chart(fig, use_container_width=True, key=f"chart_{sensor}")
                
                with col2:
                    stats = get_stats(selected_device, sensor, hours)
                    st.metric("Readings", stats['count'])
                    if stats['avg'] is not None:
                        st.metric("Avg", f"{stats['avg']:.2f}")
                        st.metric("Min", f"{stats['min']:.2f}")
                        st.metric("Max", f"{stats['max']:.2f}")
        
        # Raw data table
        st.subheader("📋 Raw Data")
        if not device_df.empty:
            display_df = device_df.copy()
            display_df["timestamp"] = display_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
            st.dataframe(
                display_df.sort_values('timestamp', ascending=False),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No rows found for this device in the selected time window.")
    else:
        st.info("No devices found. Waiting for data...")

# Auto-refresh
st.markdown(f"<p style='text-align: center; color: gray;'>Auto-refreshing every {refresh_interval}s</p>", unsafe_allow_html=True)
st.set_option('client.showErrorDetails', False)

# Auto-refresh mechanism
import time
time.sleep(refresh_interval)
rerun_streamlit()

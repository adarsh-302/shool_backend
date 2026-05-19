"""
Streamlit Dashboard - Real-time sensor data visualization (NO PANDAS)
"""
import streamlit as st
import sqlite3
import plotly.graph_objects as go

from app_compat import cutoff_timestamp, format_timestamp, rerun_streamlit, parse_timestamp

DB_FILE = "sensor_data.db"

# Page config
st.set_page_config(
    page_title="Sensor Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Sensor Data Dashboard")

def _query_rows(query, params=()):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    except sqlite3.OperationalError:
        return []

# Database query function
def get_data_raw(hours=24):
    query = '''
        SELECT timestamp, device_id, sensor_name, value, unit 
        FROM readings 
        WHERE timestamp > ?
        ORDER BY timestamp DESC
    '''
    return _query_rows(query, (cutoff_timestamp(hours),))

def get_devices():
    rows = _query_rows('SELECT DISTINCT device_id FROM readings ORDER BY device_id')
    return [row[0] for row in rows]

def get_sensors_for_device(device_id):
    rows = _query_rows(
        'SELECT DISTINCT sensor_name FROM readings WHERE device_id = ? ORDER BY sensor_name',
        (device_id,),
    )
    return [row[0] for row in rows]

def get_stats(device_id, sensor_name, hours=24):
    query = '''
        SELECT AVG(value) as avg_val, MIN(value) as min_val, MAX(value) as max_val, COUNT(*) as count
        FROM readings
        WHERE device_id = ? AND sensor_name = ? AND timestamp > ?
    '''
    rows = _query_rows(query, (device_id, sensor_name, cutoff_timestamp(hours)))
    result = rows[0] if rows else None
    
    if result and result[0] is not None:
        return {
            'avg': result[0],
            'min': result[1],
            'max': result[2],
            'count': result[3]
        }
    return {'avg': None, 'min': None, 'max': None, 'count': 0}

def get_sensor_data_for_chart(device_id, sensor_name, hours=24):
    query = '''
        SELECT timestamp, value, unit
        FROM readings
        WHERE device_id = ? AND sensor_name = ? AND timestamp > ?
        ORDER BY timestamp ASC
    '''
    rows = _query_rows(query, (device_id, sensor_name, cutoff_timestamp(hours)))
    
    parsed_rows = [(parse_timestamp(row[0]), row[1]) for row in rows]
    timestamps = [ts for ts, _ in parsed_rows if ts is not None]
    values = [value for ts, value in parsed_rows if ts is not None]
    unit = rows[0][2] if rows else ""
    
    return timestamps, values, unit

# Sidebar controls
st.sidebar.header("⚙️ Filters")
hours = st.sidebar.slider("Show data from last (hours):", 1, 168, 24)
refresh_interval = st.sidebar.slider("Auto-refresh interval (seconds):", 5, 60, 10)

# Get data
data_rows = get_data_raw(hours)
devices = get_devices()

if not data_rows:
    st.warning("⚠️ No data yet. Make sure MQTT consumer is running and publishing data.")
    st.info(f"Looking for data in: {DB_FILE}")
else:
    # Device selector
    selected_device = st.sidebar.selectbox("Select Device:", devices if devices else ["No devices"])
    
    if selected_device and selected_device != "No devices":
        sensors = get_sensors_for_device(selected_device)
        
        st.subheader(f"📊 Device: {selected_device}")
        if sensors:
            # Summary metrics
            st.subheader("📈 Summary Statistics")
            cols = st.columns(min(len(sensors), 5))
            
            for idx, sensor in enumerate(sensors):
                stats = get_stats(selected_device, sensor, hours)
                col_idx = idx % len(cols)
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
                timestamps, values, unit = get_sensor_data_for_chart(selected_device, sensor, hours)
                
                if values:
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=timestamps,
                            y=values,
                            mode='lines+markers',
                            name=sensor,
                            line=dict(color='#1f77b4', width=2),
                            marker=dict(size=6)
                        ))
                        
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
        else:
            st.info("No sensors found for this device yet.")
        
        # Raw data table
        st.subheader("📋 Raw Data")
        query = '''
            SELECT timestamp, sensor_name, value, unit
            FROM readings
            WHERE device_id = ? AND timestamp > ?
            ORDER BY timestamp DESC
            LIMIT 100
        '''
        rows = _query_rows(query, (selected_device, cutoff_timestamp(hours)))
        
        if rows:
            html = "<table style='width:100%; border-collapse: collapse;'><tr style='background-color: #f0f0f0;'>"
            html += "<th style='border: 1px solid #ddd; padding: 8px;'>Timestamp</th>"
            html += "<th style='border: 1px solid #ddd; padding: 8px;'>Sensor</th>"
            html += "<th style='border: 1px solid #ddd; padding: 8px;'>Value</th>"
            html += "<th style='border: 1px solid #ddd; padding: 8px;'>Unit</th></tr>"
            
            for row in rows:
                html += f"<tr><td style='border: 1px solid #ddd; padding: 8px;'>{format_timestamp(row[0])}</td>"
                html += f"<td style='border: 1px solid #ddd; padding: 8px;'>{row[1]}</td>"
                html += f"<td style='border: 1px solid #ddd; padding: 8px;'>{row[2]:.2f}</td>"
                html += f"<td style='border: 1px solid #ddd; padding: 8px;'>{row[3]}</td></tr>"
            
            html += "</table>"
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.info("No recent rows found for this device.")
    else:
        st.info("No devices found. Waiting for data...")

# Auto-refresh
st.markdown(f"<p style='text-align: center; color: gray;'>Auto-refreshing every {refresh_interval}s</p>", unsafe_allow_html=True)

# Auto-refresh mechanism
import time
time.sleep(refresh_interval)
rerun_streamlit()

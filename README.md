# Sensor Data Dashboard

Real-time sensor data visualization dashboard using Streamlit, powered by MQTT data collection.

## Features

- **Real-time Dashboard**: Visualize sensor data in real-time
- **MQTT Integration**: Consumes data from MQTT broker
- **SQLite Database**: Persistent data storage
- **Interactive Plots**: Plotly graphs for data visualization
- **Multi-sensor Support**: Handle multiple sensor readings

## Prerequisites

- Python 3.12+
- MQTT Broker (e.g., mqtt.dehat.co)
- Git

## Setup

### 1. Clone Repository
```bash
git clone https://github.com/adarsh-302/shool_backend.git
cd shool_backend
```

### 2. Create Virtual Environment
```bash
python -m venv sensor_env
```

### 3. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\sensor_env\Scripts\Activate.ps1
```

**Windows (Git Bash):**
```bash
source sensor_env/Scripts/activate
```

**macOS/Linux:**
```bash
source sensor_env/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

## Running Locally

### Start MQTT Consumer
```bash
python mqtt_consumer.py
```

### Start Dashboard (new terminal)
```bash
streamlit run dashboard.py
```

The dashboard will be available at `http://localhost:8501`

## Publishing Test Data

```bash
python test_publish.py
```

Or publish manually using MQTTX:
- **Topic:** `devices/device001/data`
- **Payload (JSON):**
```json
{
  "Type": "MR",
  "ID": "2002",
  "DATE": "07/01/00",
  "TIME": "23:56:34",
  "SL_ID": "1",
  "D1": "1.09",
  "D2": "1.12",
  "D3": "45.5",
  "D4": "0.8",
  "D5": "26.3",
  "D6": "2.1"
}
```

## Deploying on Streamlit Cloud

1. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
2. Click **New app**
3. Select:
   - **Repository:** `adarsh-302/shool_backend`
   - **Branch:** `main`
   - **Main file path:** `dashboard.py`
4. Click **Deploy**

## Configuration

MQTT Broker details in `mqtt_consumer.py`:
- Host: `mqtt.dehat.co`
- Port: `1883`
- Username: `charan`
- Password: `mqtt@2026`

## Database

- **File:** `sensor_data.db`
- **Table:** `readings`
- **Columns:** timestamp, device_id, device_type, sensor_name, value, unit, date_field, time_field

## Troubleshooting

**No data showing:**
- Ensure MQTT consumer is running
- Check MQTT broker connectivity
- Verify sensor is publishing to `devices/device001/data` topic

**ImportError for packages:**
- Run: `pip install -r requirements.txt`
- Ensure virtual environment is activated

## License

MIT

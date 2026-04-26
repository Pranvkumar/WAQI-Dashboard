# WAQI-Dashboard

India-focused real-time air quality dashboard built with Streamlit using the WAQI API.
Git-https://github.com/Pranvkumar/WAQI-Dashboard

## Features

- India-only city comparison (Delhi, Mumbai, Kolkata, Bengaluru, and more)
- Live AQI, PM1, PM2.5, PM10, temperature, humidity, pressure, wind, rain, and gas monitoring
- Plotly visualizations:
	- AQI severity bar chart
	- PM2.5 vs temperature bubble chart
- Summary cards for core air-quality and weather measurements
- Cached API fetching with graceful error handling

## Project Files

- `app.py`: Main Streamlit dashboard app
- `requirements.txt`: Python dependencies
- `.env.example`: Environment variable template

## Data Fields

The dashboard currently surfaces AQI, PM1, PM2.5, PM10, temperature, humidity, pressure, wind speed, wind direction, rain, CO, NO2, O3, and SO2 when the WAQI station provides them.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure API token in `.env`:

```env
WAQI_TOKEN=your_waqi_api_token_here
```

## Run

```bash
streamlit run app.py
```

Open the local Streamlit URL shown in the terminal (typically `http://localhost:8501`).

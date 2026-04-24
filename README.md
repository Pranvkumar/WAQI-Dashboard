# WAQI-Dashboard

India-focused real-time air quality dashboard built with Streamlit using the WAQI API.

## Features

- India-only city comparison (Delhi, Mumbai, Kolkata, Bengaluru, and more)
- Live AQI, PM2.5, PM10, temperature, and humidity monitoring
- Plotly visualizations:
	- AQI severity bar chart
	- PM2.5 vs temperature bubble chart
- 8 key metric cards for quick insights
- Cached API fetching with graceful error handling

## Project Files

- `app.py`: Main Streamlit dashboard app
- `requirements.txt`: Python dependencies
- `.env.example`: Environment variable template
- `sample.py`: Initial prototype file

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
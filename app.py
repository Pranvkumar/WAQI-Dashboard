from __future__ import annotations

import os
from typing import Any

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from dotenv import load_dotenv

# Load token from environment variables (.env)
load_dotenv()
API_TOKEN = os.getenv("WAQI_TOKEN")

st.set_page_config(page_title="India Air Quality Dashboard", layout="wide")

INDIA_CITIES: list[str] = [
    "delhi",
    "mumbai",
    "kolkata",
    "chennai",
    "bengaluru",
    "hyderabad",
    "pune",
    "ahmedabad",
    "jaipur",
    "lucknow",
    "kanpur",
    "patna",
]


def to_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def extract_iaqi_value(iaqi: dict[str, Any], key: str) -> float | None:
    return to_float(iaqi.get(key, {}).get("v"))


def classify_aqi(aqi_value: float | None) -> str:
    if aqi_value is None:
        return "Unknown"
    if aqi_value <= 50:
        return "Good"
    if aqi_value <= 100:
        return "Moderate"
    if aqi_value <= 150:
        return "Unhealthy (Sensitive)"
    if aqi_value <= 200:
        return "Unhealthy"
    if aqi_value <= 300:
        return "Very Unhealthy"
    return "Hazardous"


@st.cache_data(ttl=1800)
def fetch_waqi_data(cities: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    if not API_TOKEN:
        return pd.DataFrame()

    for city in cities:
        endpoint = f"https://api.waqi.info/feed/{city}/?token={API_TOKEN}"
        try:
            response = requests.get(endpoint, timeout=15)
            response.raise_for_status()
            payload = response.json()

            if payload.get("status") != "ok":
                continue

            data = payload.get("data", {})
            iaqi = data.get("iaqi", {})

            aqi = to_float(data.get("aqi"))
            pm25 = extract_iaqi_value(iaqi, "pm25")
            pm10 = extract_iaqi_value(iaqi, "pm10")
            pm1 = extract_iaqi_value(iaqi, "pm1")
            temp = extract_iaqi_value(iaqi, "t")
            humidity = extract_iaqi_value(iaqi, "h")
            pressure = extract_iaqi_value(iaqi, "p")
            wind_speed = extract_iaqi_value(iaqi, "w")
            wind_direction = extract_iaqi_value(iaqi, "wd")
            rain = extract_iaqi_value(iaqi, "r")
            co = extract_iaqi_value(iaqi, "co")
            no2 = extract_iaqi_value(iaqi, "no2")
            o3 = extract_iaqi_value(iaqi, "o3")
            so2 = extract_iaqi_value(iaqi, "so2")

            rows.append(
                {
                    "City": city.title(),
                    "AQI": aqi,
                    "PM1": pm1,
                    "PM2.5": pm25,
                    "PM10": pm10,
                    "Temperature (C)": temp,
                    "Humidity (%)": humidity,
                    "Pressure (hPa)": pressure,
                    "Wind Speed (m/s)": wind_speed,
                    "Wind Direction (deg)": wind_direction,
                    "Rain (mm)": rain,
                    "CO (µg/m³)": co,
                    "NO2 (µg/m³)": no2,
                    "O3 (µg/m³)": o3,
                    "SO2 (µg/m³)": so2,
                    "Station": data.get("city", {}).get("name", "Unknown"),
                    "Updated": data.get("time", {}).get("s", "N/A"),
                }
            )
        except (requests.RequestException, ValueError):
            continue

    return pd.DataFrame(rows)


st.title("India Real-Time Air Quality Dashboard")
st.caption("Live WAQI monitoring for major Indian cities")

st.sidebar.header("Controls")
selected_cities = st.sidebar.multiselect(
    "Select Indian cities",
    INDIA_CITIES,
    default=["delhi", "mumbai", "kolkata", "bengaluru"],
)

if st.sidebar.button("Refresh Data"):
    st.cache_data.clear()

if not API_TOKEN:
    st.error("Missing WAQI_TOKEN. Add it in your .env file.")
    st.stop()

if not selected_cities:
    st.info("Select at least one city from the sidebar to view data.")
    st.stop()

with st.spinner("Fetching latest WAQI data for India..."):
    df = fetch_waqi_data(selected_cities)

if df.empty:
    st.warning("No valid data returned for selected cities. Try refresh or different cities.")
    st.stop()

numeric_cols = ["AQI", "PM2.5", "PM10", "Temperature (C)", "Humidity (%)"]
numeric_cols.extend(
    [
        "PM1",
        "Pressure (hPa)",
        "Wind Speed (m/s)",
        "Wind Direction (deg)",
        "Rain (mm)",
        "CO (µg/m³)",
        "NO2 (µg/m³)",
        "O3 (µg/m³)",
        "SO2 (µg/m³)",
    ]
)
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df["AQI Category"] = df["AQI"].apply(classify_aqi)

st.subheader("Key Insights")
col1, col2, col3, col4 = st.columns(4)
col5, col6, col7, col8 = st.columns(4)

highest_aqi = df.loc[df["AQI"].idxmax()] if df["AQI"].notna().any() else None
lowest_aqi = df.loc[df["AQI"].idxmin()] if df["AQI"].notna().any() else None

col1.metric("Cities Tracked", f"{len(df)}")
col2.metric("Avg AQI", f"{df['AQI'].mean():.1f}" if df["AQI"].notna().any() else "N/A")
col3.metric("Avg PM2.5", f"{df['PM2.5'].mean():.1f}" if df["PM2.5"].notna().any() else "N/A")
col4.metric("Avg Temperature", f"{df['Temperature (C)'].mean():.1f} C" if df["Temperature (C)"].notna().any() else "N/A")
col5.metric("Highest AQI City", highest_aqi["City"] if highest_aqi is not None else "N/A")
col6.metric("Lowest AQI City", lowest_aqi["City"] if lowest_aqi is not None else "N/A")
col7.metric("Max PM2.5", f"{df['PM2.5'].max():.1f}" if df["PM2.5"].notna().any() else "N/A")
col8.metric("Avg Humidity", f"{df['Humidity (%)'].mean():.1f}%" if df["Humidity (%)"].notna().any() else "N/A")

st.subheader("Additional Measurements")
extra1, extra2, extra3, extra4 = st.columns(4)
extra5, extra6, extra7, extra8 = st.columns(4)

extra1.metric("Avg Pressure", f"{df['Pressure (hPa)'].mean():.1f} hPa" if df["Pressure (hPa)"].notna().any() else "N/A")
extra2.metric("Avg Wind Speed", f"{df['Wind Speed (m/s)'].mean():.1f} m/s" if df["Wind Speed (m/s)"].notna().any() else "N/A")
extra3.metric("Avg Wind Direction", f"{df['Wind Direction (deg)'].mean():.1f}°" if df["Wind Direction (deg)"].notna().any() else "N/A")
extra4.metric("Avg Rain", f"{df['Rain (mm)'].mean():.1f} mm" if df["Rain (mm)"].notna().any() else "N/A")
extra5.metric("Avg PM1", f"{df['PM1'].mean():.1f}" if df["PM1"].notna().any() else "N/A")
extra6.metric("Avg CO", f"{df['CO (µg/m³)'].mean():.1f}" if df["CO (µg/m³)"].notna().any() else "N/A")
extra7.metric("Avg NO2", f"{df['NO2 (µg/m³)'].mean():.1f}" if df["NO2 (µg/m³)"].notna().any() else "N/A")
extra8.metric("Avg O3", f"{df['O3 (µg/m³)'].mean():.1f}" if df["O3 (µg/m³)"].notna().any() else "N/A")

st.divider()
left, right = st.columns(2)

with left:
    st.subheader("AQI Comparison Across Selected Indian Cities")
    fig_aqi = px.bar(
        df,
        x="City",
        y="AQI",
        color="AQI Category",
        category_orders={
            "AQI Category": [
                "Good",
                "Moderate",
                "Unhealthy (Sensitive)",
                "Unhealthy",
                "Very Unhealthy",
                "Hazardous",
                "Unknown",
            ]
        },
        color_discrete_map={
            "Good": "#2E7D32",
            "Moderate": "#F9A825",
            "Unhealthy (Sensitive)": "#EF6C00",
            "Unhealthy": "#C62828",
            "Very Unhealthy": "#6A1B9A",
            "Hazardous": "#4E342E",
            "Unknown": "#607D8B",
        },
    )
    fig_aqi.update_layout(xaxis_title="City", yaxis_title="AQI")
    st.plotly_chart(fig_aqi, use_container_width=True)

with right:
    st.subheader("PM2.5 vs Temperature")
    scatter_df = df.dropna(subset=["PM2.5", "Temperature (C)", "AQI"]) 
    if scatter_df.empty:
        st.info("Not enough PM2.5 and Temperature data for selected cities.")
    else:
        fig_scatter = px.scatter(
            scatter_df,
            x="Temperature (C)",
            y="PM2.5",
            size="AQI",
            color="City",
            hover_name="Station",
            title="Relationship Between Temperature and PM2.5",
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

st.subheader("Live Data Table")
st.dataframe(
    df[[
        "City",
        "AQI",
        "AQI Category",
        "PM1",
        "PM2.5",
        "PM10",
        "Temperature (C)",
        "Humidity (%)",
        "Pressure (hPa)",
        "Wind Speed (m/s)",
        "Wind Direction (deg)",
        "Rain (mm)",
        "CO (µg/m³)",
        "NO2 (µg/m³)",
        "O3 (µg/m³)",
        "SO2 (µg/m³)",
        "Station",
        "Updated",
    ]],
    use_container_width=True,
)

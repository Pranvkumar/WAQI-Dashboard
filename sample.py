import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import os
from dotenv import load_dotenv

# Load environment variables (Create a .env file in your folder with WAQI_TOKEN=your_token_here)
load_dotenv()
API_TOKEN = os.getenv('WAQI_TOKEN')

# Page Configuration
st.set_page_config(page_title="Global Air Quality Dashboard", page_icon="🌍", layout="wide")

@st.cache_data(ttl=3600) # Cache data for 1 hour to save API calls
def fetch_waqi_data(cities):
    data_list = []
    if not API_TOKEN:
        st.error("API Token missing. Please add WAQI_TOKEN to your .env file.")
        return pd.DataFrame()

    for city in cities:
        url = f"https://api.waqi.info/feed/{city}/?token={API_TOKEN}"
        try:
            response = requests.get(url).json()
            if response['status'] == 'ok':
                data = response['data']
                
                # Extracting available data (handling missing keys safely)
                iaqi = data.get('iaqi', {})
                pm25 = iaqi.get('pm25', {}).get('v', None)
                pm10 = iaqi.get('pm10', {}).get('v', None)
                temp = iaqi.get('t', {}).get('v', None)
                humidity = iaqi.get('h', {}).get('v', None)

                data_list.append({
                    'City': city.capitalize(),
                    'AQI': data.get('aqi', 0),
                    'PM2.5': pm25,
                    'PM10': pm10,
                    'Temperature (°C)': temp,
                    'Humidity (%)': humidity,
                    'Station': data.get('city', {}).get('name', 'Unknown')
                })
        except Exception as e:
            st.warning(f"Failed to fetch data for {city}: {e}")
            
    return pd.DataFrame(data_list)

# --- UI Layout ---
st.title("🌍 Real-Time Environmental Data Dashboard")
st.markdown("Analyzing live Air Quality Index (AQI) and climate metrics across major global cities.")

# Sidebar Selection
st.sidebar.header("Dashboard Controls")
default_cities = ['delhi', 'london', 'new york', 'beijing', 'los angeles', 'tokyo', 'paris', 'sydney']
selected_cities = st.sidebar.multiselect("Select Cities to Compare", default_cities, default=['delhi', 'london', 'new york', 'beijing'])

if st.sidebar.button("Refresh Data"):
    st.cache_data.clear()

# --- Main Dashboard Logic ---
if selected_cities:
    with st.spinner("Fetching live environmental data..."):
        df = fetch_waqi_data(selected_cities)

    if not df.empty:
        # 1. Key Insights (Metrics)
        st.subheader("Key Global Insights")
        col1, col2, col3, col4 = st.columns(4)
        
        highest_aqi = df.loc[df['AQI'].idxmax()]
        lowest_aqi = df.loc[df['AQI'].idxmin()]
        avg_pm25 = df['PM2.5'].mean()
        
        col1.metric("Highest Pollution", highest_aqi['City'], f"AQI: {highest_aqi['AQI']}", delta_color="inverse")
        col2.metric("Cleanest Air", lowest_aqi['City'], f"AQI: {lowest_aqi['AQI']}")
        col3.metric("Avg Global PM2.5", f"{avg_pm25:.1f}")
        col4.metric("Total Cities Tracked", len(df))

        st.divider()

        # 2. Visualizations
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.subheader("AQI City Comparison")
            # Create color mapping based on AQI severity
            df['Condition'] = pd.cut(pd.to_numeric(df['AQI'], errors='coerce'), 
                                     bins=[0, 50, 100, 150, 200, 300, 1000], 
                                     labels=['Good', 'Moderate', 'Unhealthy (Sensitive)', 'Unhealthy', 'Very Unhealthy', 'Hazardous'])
            
            fig1 = px.bar(df, x='City', y='AQI', color='Condition', 
                          color_discrete_map={'Good': 'green', 'Moderate': 'yellow', 'Unhealthy (Sensitive)': 'orange', 'Unhealthy': 'red', 'Very Unhealthy': 'purple', 'Hazardous': 'maroon'},
                          title="Current Air Quality Index by City")
            st.plotly_chart(fig1, use_container_width=True)

        with col_chart2:
            st.subheader("Pollution vs. Temperature")
            fig2 = px.scatter(df, x='Temperature (°C)', y='PM2.5', size='AQI', color='City', hover_name='Station',
                              title="Impact of Temperature on PM2.5 Levels")
            st.plotly_chart(fig2, use_container_width=True)

        # 3. Raw Data Table
        st.subheader("Live Dataset")
        st.dataframe(df.style.background_gradient(subset=['AQI'], cmap='Reds'))

else:
    st.info("Please select at least one city from the sidebar to begin analysis.")
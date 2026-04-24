# **Context**

I am building an interactive Environmental Data Dashboard using Streamlit for my university project. The goal is to analyze real-time air quality (AQI) and climate data across multiple global cities to extract business/sustainability insights.

# **Data Source**

Use the live WAQI (World Air Quality Index) API. The endpoint format is:

https://api.waqi.info/feed/{city}/?token={api\_token}

# **Requirements for the Streamlit App (app.py)**

1. **Security:** Use python-dotenv to load the WAQI API token from a .env file (os.getenv('WAQI\_TOKEN')). Do not hardcode the API key.  
2. **Data Fetching:** Create a caching function (@st.cache\_data) that accepts a list of cities (e.g., Delhi, London, New York, Beijing, Los Angeles, Tokyo) and fetches their current AQI, PM2.5, Temperature, and Humidity from the WAQI API. Handle API errors gracefully.  
3. **UI Layout:** \- Add a clean title and sidebar.  
   * In the sidebar, allow the user to select which cities to compare using st.multiselect.  
4. **Visualizations (Use Plotly):**  
   * **City Comparison:** A Plotly Bar Chart comparing the overall AQI of the selected cities. Color-code the bars based on AQI severity (Good, Moderate, Unhealthy).  
   * **Pollutant Breakdown:** A Scatter plot or Bubble chart showing PM2.5 vs Temperature for the selected cities.  
5. **Key Insights (6-8 metrics):** Use st.metric columns to display the highest AQI city, lowest AQI city, average global PM2.5, and other key data points derived from the dataframe.  
6. **Code Quality:** Ensure the code is well-commented, strictly typed where possible, and handles missing JSON keys if a city station lacks specific sensor data (like PM10 or Temp).
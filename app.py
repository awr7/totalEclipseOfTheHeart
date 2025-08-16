import streamlit as st
import geopandas as gpd
import pydeck as pdk
import pandas as pd
import pytz

# My Awesome Title
st.title("Solar Eclipse Path Visualizer")

# Load shapefile
shapefile_path = './data/umbra_lo.shp'
gdf = gpd.read_file(shapefile_path, engine="pyogrio")

# Convert UTCTime to datetime with UTC timezone, then to Eastern Time (ET)
gdf['UTCTime'] = pd.to_datetime(gdf['UTCTime'], format='%H:%M:%S').dt.tz_localize('UTC').dt.tz_convert('America/New_York')

# Ad a hour because daylight saving
gdf['UTCTime'] = gdf['UTCTime'] + pd.Timedelta(hours=1)


# Sort the times as datetime objects or else it glitches!
gdf = gdf.sort_values(by='UTCTime')

# Change it to 12hour instead of 24 hours
gdf['ESTTime'] = gdf['UTCTime'].dt.strftime('%I:%M:%S %p')
unique_times = gdf['ESTTime'].unique()

# Create a slider for time selection
selected_time = st.select_slider("Select Time (EST)", options=unique_times)

# Filter the GeoDataFrame for the selected time
selected_gdf = gdf[gdf['ESTTime'] == selected_time]

# Shadow layer 
shadow_layer = pdk.Layer(
    "GeoJsonLayer",
    gdf,
    opacity=0.5,
    stroked=True,
    filled=True,
    get_line_color=[255, 255, 255],
    get_fill_color=[200, 200, 200], 
)

# Umbra layer (black fill with yellow border)
umbra_layer = pdk.Layer(
    "GeoJsonLayer",
    selected_gdf,
    stroked=True,
    filled=True,
    get_line_color=[255, 255, 0],
    get_fill_color=[0, 0, 0],
    line_width_min_pixels=2,
)

# Update when we move slider
if selected_time == unique_times[0]:
    view_state = pdk.ViewState(latitude=39.8283, longitude=-98.5795, zoom=3)
else:
    # Update view based on the selected time's umbra location
    view_state = pdk.ViewState(
        latitude=selected_gdf['CenterLat'].mean(), 
        longitude=selected_gdf['CenterLon'].mean(), 
        zoom=3
    )

r = pdk.Deck(layers=[shadow_layer, umbra_layer], initial_view_state=view_state)
st.pydeck_chart(r)

st.write("""
This app visualizes the path of the solar eclipse, using data from NASA's Eclipse Explorer. 
Select a time using the slider to view the eclipse's umbra location on the map. 
For more information on the data used, visit [NASA's Eclipse Explorer](https://eclipse-explorer.smce.nasa.gov/).
""")

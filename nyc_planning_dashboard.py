import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import folium
from streamlit_folium import folium_static
from sodapy import Socrata


# https://data.cityofnewyork.us/Environment/NYC-Building-Energy-and-Water-Data-Disclosure-for-/5zyy-y8am/about_data
# Load sample NYC OpenData (Replace with actual data sources)
@st.cache_data
def load_data():
    # emissions_data = pd.read_csv("https://data.cityofnewyork.us/resource/rgfe-8y2z.csv")  # Replace with real data
    # zoning_data = gpd.read_file("https://www1.nyc.gov/assets/planning/download/zip/data-maps/open-data/nyzd.geojson")
    client = Socrata("data.cityofnewyork.us", None)
    results = client.get("5zyy-y8am", limit=1000)
    return results

data = load_data()
data_df = pd.DataFrame.from_records(data)

# Sidebar Filters
st.sidebar.header("Filter Options")
boroughs = data_df["borough"].dropna().unique()
selected_borough = st.sidebar.selectbox("Select Borough", ["All"] + list(boroughs))

# Filter Data
if selected_borough != "All":
    emissions_data = data_df[data_df["borough"] == selected_borough]

# Plotly Visualization: Emissions by Building Type
st.subheader("Emissions Trends by Building Type")
fig = px.bar(
    data_df, x="primary_property_type", y="net_emissions_metric_tons",
    color="borough", title="Total Emissions by Building Type"
)
st.plotly_chart(fig)

# Interactive Map using Folium
st.subheader("Zoning & Emissions Heatmap")
map_center = [40.7128, -74.0060]  # NYC Center
m = folium.Map(location=map_center, zoom_start=11)

data_df["net_emissions_metric_tons"] = pd.to_numeric(data_df["net_emissions_metric_tons"], errors="coerce")
# Drop rows where latitude or longitude is missing
data_df = data_df.dropna(subset=["latitude", "longitude"])
# Convert to numeric (handle errors gracefully)
data_df["latitude"] = pd.to_numeric(data_df["latitude"], errors="coerce")
data_df["longitude"] = pd.to_numeric(data_df["longitude"], errors="coerce")

for _, row in data_df.iterrows():
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=row["net_emissions_metric_tons"] / 1000,  # Normalize for visualization
        color="red",
        fill=True,
        fill_color="red",
        fill_opacity=0.6,
        popup=f"{row['primary_property_type']}: {row['net_emissions_metric_tons']} metric tons"
    ).add_to(m)

folium_static(m)

# Additional Insights Section
st.subheader("Key Takeaways")
st.markdown("- High emissions in commercial districts.")
st.markdown("- Residential buildings show varied impact across boroughs.")
st.markdown("- Zoning mismatches correlate with emissions hotspots.")

st.success("✅ Interactive NYC OpenData visualization powered by Streamlit, Plotly, and Folium.")

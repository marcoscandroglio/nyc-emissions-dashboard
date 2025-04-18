import os
import numpy as np
import branca.colormap as cm
import streamlit as st

st.markdown(
    """
    <style>
        /* Expand overall width */
        html, body, [data-testid="stAppViewContainer"], .main, .block-container {
            max-width: 100vw !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }

        /* Optional: Adjust chart canvas if still too narrow */
        .element-container:has([data-testid="stPlotlyChart"]) {
            width: 100% !important;
        }
        /* Expand the folium map container */
        .folium-map {
            width: 95% !important;
            height: 700px !important; /* You can adjust height */
        }
    </style>
    """,
    unsafe_allow_html=True
)

import pandas as pd
import geopandas as gpd
import plotly.express as px
import folium
# from streamlit_folium import folium_static
import streamlit.components.v1 as components
from sodapy import Socrata


# https://data.cityofnewyork.us/Environment/NYC-Building-Energy-and-Water-Data-Disclosure-for-/5zyy-y8am/about_data
# Load sample NYC OpenData (Replace with actual data sources)
@st.cache_data
def load_data():
    csv_path = "data.csv"

    if os.path.exists(csv_path):
        st.info("📂 Loading data from local CSV cache...")
        return pd.read_csv(csv_path)

    st.info("🌐 Fetching data from NYC OpenData API...")
    client = Socrata("data.cityofnewyork.us", None)
    dataset_id = "5zyy-y8am"
    limit = 1000
    offset = 0
    results = []

    progress_bar = st.progress(0)
    i = 0

    while True:
        batch = client.get(dataset_id, limit=limit, offset=offset)
        if not batch:
            break
        results.extend(batch)
        offset += limit
        i += 1
        progress_bar.progress(min(i / 50, 1.0))  # Assumes ~50k rows total

    progress_bar.empty()

    df = pd.DataFrame.from_records(results)
    df.to_csv(csv_path, index=False)
    return df

data_df = load_data()
# data_df = pd.DataFrame.from_records(data)

# # Sidebar Filters
# st.sidebar.header("Filter Options")
# boroughs = data_df["borough"].dropna().unique()
# selected_borough = st.sidebar.selectbox("Select Borough", ["All"] + list(boroughs))

# # Filter Data
# if selected_borough != "All":
#     emissions_data = data_df[data_df["borough"] == selected_borough]

# # Plotly Visualization: Emissions by Building Type
# st.subheader("Emissions Trends by Building Type")
# fig = px.bar(
#     data_df, x="primary property type", y="net emissions - metric tons",
#     color="borough", title="Total Emissions by Building Type",
#     height=800
# )

# fig.update_layout(
#     xaxis_tickangle=30
# )

# st.plotly_chart(fig)

# Interactive Map using Folium
st.subheader("Zoning & Emissions Heatmap")
map_center = [40.7128, -74.0060]  # NYC Center
m = folium.Map(location=map_center, zoom_start=12, tiles="CartoDB dark_matter")

# Ensure emissions are numeric
data_df["net_emissions_metric_tons"] = pd.to_numeric(data_df["net_emissions_metric_tons"], errors="coerce")

# Filter out rows with invalid coordinates or emissions
data_df = data_df.dropna(subset=["latitude", "longitude", "net_emissions_metric_tons"])
data_df["latitude"] = pd.to_numeric(data_df["latitude"], errors="coerce")
data_df["longitude"] = pd.to_numeric(data_df["longitude"], errors="coerce")
data_df = data_df.dropna(subset=["latitude", "longitude"])

# Filter out negative and extreme outlier emissions
filtered_df = data_df[
    (data_df["net_emissions_metric_tons"] >= 0) &
    (data_df["net_emissions_metric_tons"] <= 200000)
]

filtered_df = filtered_df.sort_values("net_emissions_metric_tons", ascending=True)

# Compute log(emissions + 1) to avoid log(0)
filtered_df["log_emissions"] = filtered_df["net_emissions_metric_tons"].apply(lambda x: np.log10(x + 1))

min_log, max_log = filtered_df["log_emissions"].min(), filtered_df["log_emissions"].max()
st.write("Log emissions range:", min_log, "to", max_log)

# Use log-emissions for color scaling
colormap = cm.linear.YlOrRd_09.scale(min_log, max_log)
colormap.caption = "Log(Net Emissions + 1)"
colormap.add_to(m)

# Add markers
for _, row in filtered_df.iterrows():
    log_val = row["log_emissions"]
    raw_val = row["net_emissions_metric_tons"]
    color = colormap(log_val)

    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=1.5,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.8,
        popup=f"{row['primary_property_type']}: {raw_val:.2f} metric tons"
    ).add_to(m)

# folium_static(m)
# Render Folium map manually with full width
map_html = m.get_root().render()

components.html(map_html, height=1400, width=1600)  # Adjust width as needed

# Aggregate emissions by property type and borough
emissions_grouped = (
    data_df.groupby(["primary_property_type", "borough"], observed=True)["net_emissions_metric_tons"]
    .sum()
    .reset_index()
)

# Compute total emissions per property type
total_by_type = (
    emissions_grouped.groupby("primary_property_type")["net_emissions_metric_tons"]
    .sum()
    .sort_values(ascending=False)
)

# Get the correct sorted category order
sorted_types = total_by_type.index.tolist()

# Re-assign categorical x-axis with ordered property types
emissions_grouped["primary_property_type"] = pd.Categorical(
    emissions_grouped["primary_property_type"],
    categories=sorted_types,
    ordered=True
)

# Re-sort DataFrame so Plotly respects category order
emissions_grouped = emissions_grouped.sort_values("primary_property_type")

# Plot
fig = px.bar(
    emissions_grouped,
    x="primary_property_type",
    y="net_emissions_metric_tons",
    color="borough",
    title="Total Emissions by Building Type and Borough",
    height=800
)

fig.update_layout(
    xaxis_tickangle=30
)

st.subheader("Emissions Trends by Building Type")
st.plotly_chart(fig)

st.success("✅ Interactive NYC OpenData visualization powered by Streamlit, Plotly, and Folium.")

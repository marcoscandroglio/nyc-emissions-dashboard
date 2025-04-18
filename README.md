# NYC Building Emissions Dashboard

This Streamlit app visualizes building-level emissions data for New York City. It uses data from the NYC OpenData platform to generate an interactive heatmap and emissions breakdown by building type and borough.

## Features

- Interactive map of emissions using Folium with a dark basemap
- Borough-level breakdown of emissions for each building type
- Logarithmic color scaling for better contrast across emission levels
- Automatically fetches and caches data from NYC OpenData
- Responsive layout with wide-format bar charts and full-width map display

## Data Source

This app uses the NYC Building Energy and Water Data Disclosure dataset from NYC OpenData:  
https://data.cityofnewyork.us/Environment/NYC-Building-Energy-and-Water-Data-Disclosure-for-/5zyy-y8am/about_data

## Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/nyc-planning-dashboard.git
   cd nyc-planning-dashboard
2. (Optional) Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
5. Run the app:
   ```bash
   streamlit run app.py


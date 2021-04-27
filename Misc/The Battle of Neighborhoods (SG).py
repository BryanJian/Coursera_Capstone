# %% [markdown]
# # The Battle of the Neighbourhoods - Capstone Project  <a class="tocSkip">
# ## Applied Data Science Course by IBM @ Coursera <a class="tocSkip">
#
# Author: Bryan Choi
# %% [markdown]
# <h1>Table of Contents<span class="tocSkip"></span></h1>
# <div class="toc"><ul class="toc-item"><li><span><a href="#Executive-Summary-" data-toc-modified-id="Executive-Summary--1"><span class="toc-item-num">1&nbsp;&nbsp;</span>Executive Summary <a class="anchor" id="executive-summary"></a></a></span></li><li><span><a href="#Introduction:-Business-Problem" data-toc-modified-id="Introduction:-Business-Problem-2"><span class="toc-item-num">2&nbsp;&nbsp;</span>Introduction: Business Problem</a></span></li><li><span><a href="#Data" data-toc-modified-id="Data-3"><span class="toc-item-num">3&nbsp;&nbsp;</span>Data</a></span><ul class="toc-item"><li><span><a href="#GeoJSON,-Population,-Income-Data-Preparation" data-toc-modified-id="GeoJSON,-Population,-Income-Data-Preparation-3.1"><span class="toc-item-num">3.1&nbsp;&nbsp;</span>GeoJSON, Population, Income Data Preparation</a></span><ul class="toc-item"><li><span><a href="#Load-Singapore-Planning-Area-Boundaries" data-toc-modified-id="Load-Singapore-Planning-Area-Boundaries-3.1.1"><span class="toc-item-num">3.1.1&nbsp;&nbsp;</span>Load Singapore Planning Area Boundaries</a></span></li><li><span><a href="#Load-Population-Data" data-toc-modified-id="Load-Population-Data-3.1.2"><span class="toc-item-num">3.1.2&nbsp;&nbsp;</span>Load Population Data</a></span></li><li><span><a href="#Load-Income-Data" data-toc-modified-id="Load-Income-Data-3.1.3"><span class="toc-item-num">3.1.3&nbsp;&nbsp;</span>Load Income Data</a></span></li><li><span><a href="#Load-Flat-Resale-Price-Data" data-toc-modified-id="Load-Flat-Resale-Price-Data-3.1.4"><span class="toc-item-num">3.1.4&nbsp;&nbsp;</span>Load Flat Resale Price Data</a></span></li></ul></li><li><span><a href="#Bubble-Tea-Shop-Coordinates" data-toc-modified-id="Bubble-Tea-Shop-Coordinates-3.2"><span class="toc-item-num">3.2&nbsp;&nbsp;</span>Bubble Tea Shop Coordinates</a></span><ul class="toc-item"><li><span><a href="#Scraping-Xing-Fu-Tang-Addresses-from-Homepage" data-toc-modified-id="Scraping-Xing-Fu-Tang-Addresses-from-Homepage-3.2.1"><span class="toc-item-num">3.2.1&nbsp;&nbsp;</span>Scraping Xing Fu Tang Addresses from Homepage</a></span></li><li><span><a href="#Foursquare-API-Credentials" data-toc-modified-id="Foursquare-API-Credentials-3.2.2"><span class="toc-item-num">3.2.2&nbsp;&nbsp;</span>Foursquare API Credentials</a></span></li><li><span><a href="#API-Request-for-Bubble-Tea-Locations" data-toc-modified-id="API-Request-for-Bubble-Tea-Locations-3.2.3"><span class="toc-item-num">3.2.3&nbsp;&nbsp;</span>API Request for Bubble Tea Locations</a></span></li></ul></li><li><span><a href="#Geospatial-Visualisation" data-toc-modified-id="Geospatial-Visualisation-3.3"><span class="toc-item-num">3.3&nbsp;&nbsp;</span>Geospatial Visualisation</a></span><ul class="toc-item"><li><span><a href="#Plot-of-Xing-Fu-Tang-Location-vs.-Locations-of-Other-Bubble-Tea-Shop" data-toc-modified-id="Plot-of-Xing-Fu-Tang-Location-vs.-Locations-of-Other-Bubble-Tea-Shop-3.3.1"><span class="toc-item-num">3.3.1&nbsp;&nbsp;</span>Plot of Xing Fu Tang Location vs. Locations of Other Bubble Tea Shop</a></span></li></ul></li></ul></li><li><span><a href="#Methodology" data-toc-modified-id="Methodology-4"><span class="toc-item-num">4&nbsp;&nbsp;</span>Methodology</a></span></li><li><span><a href="#Analysis" data-toc-modified-id="Analysis-5"><span class="toc-item-num">5&nbsp;&nbsp;</span>Analysis</a></span></li><li><span><a href="#Results-and-Discussion" data-toc-modified-id="Results-and-Discussion-6"><span class="toc-item-num">6&nbsp;&nbsp;</span>Results and Discussion</a></span></li><li><span><a href="#Conclusion" data-toc-modified-id="Conclusion-7"><span class="toc-item-num">7&nbsp;&nbsp;</span>Conclusion</a></span></li><li><span><a href="#Reference" data-toc-modified-id="Reference-8"><span class="toc-item-num">8&nbsp;&nbsp;</span>Reference</a></span></li></ul></div>
# %% [markdown]
# ## Executive Summary <a class="anchor" id="executive-summary"></a>
# %% [markdown]
# ## Introduction: Business Problem
# %% [markdown]
# ## Data
# %% [markdown]
# Import Necessary Libraries

import os
import folium
import geopandas as gpd
import numpy as np
import pandas as pd
import requests  # library to handle requests
from branca.element import MacroElement, Template
from bs4 import BeautifulSoup
from folium.plugins import HeatMap
from geopy.geocoders import (
    Nominatim,
)  # module to convert an address into latitude and longitude values
from IPython import get_ipython
from matplotlib import cm
from matplotlib.colors import Normalize, rgb2hex
from shapely.geometry.collection import GeometryCollection
from shapely.geometry.multipolygon import MultiPolygon

# %% [markdown]
# ### GeoJSON, Population, Income Data Preparation
# %% [markdown]
# #### Load Singapore Planning Area Boundaries

# %%
# Geodata Wrangle
sing_geo = r"MP14_PLNG_AREA_NO_SEA_PL.geojson"  # Geodata

# GeoDataFrame
geodf = gpd.read_file(sing_geo)
geodf = geodf[["name", "id", "geometry"]]
geodf = geodf.rename(columns={"name": "Planning Area"})

# Converting GeometryCollection to Multipolygon to support Planning Areas with islands
geodf["geometry"] = [
    MultiPolygon([feature]) if isinstance(feature, GeometryCollection) else feature
    for feature in geodf["geometry"]
]  # Required or else highlight function does not work

# Tooltip style function
style_function = lambda x: {
    "fillColor": "#ffffff",
    "color": "#488776",
    "fillOpacity": 0.1,
    "weight": 0.5,
}

# Planning Area highlight function
highlight_function = lambda x: {
    "fillColor": "#000000",
    "color": "#000000",
    "fillOpacity": 0.50,
    "weight": 0.1,
}

# %% [markdown]
# #### Load Population Data

# %%
# Population Data Wrangle
popdf = pd.read_csv("SG_planningarea_pop.csv")  # Population data
# Merging DFs and saving
geopop = geodf.merge(popdf, on="Planning Area")
geopop.to_csv("SG_planningarea_geopop.csv", index=False)

popdf.head()

# %% [markdown]
# #### Load Income Data

# %%
# Income Data Wrangle
fincdf = pd.read_csv("SG_planningarea_inc.csv")
incdf_cs = pd.read_csv("SG_planningarea_inc.csv")
incdf_cs.loc[:, fincdf.columns != "Planning Area"] = incdf_cs.loc[
    :, fincdf.columns != "Planning Area"
].cumsum(axis=1)

# Cumulative Planning Area Median Pop
incdf_cs["cum_med_pop"] = fincdf.sum(axis=1, numeric_only=True) / 2

# Identifying median income bracket by Planning Area
inc_brackets = [
    "Below $1,000",
    "$1,000 - $1,499",
    "$1,500 - $1,999",
    "$2,000 - $2,499",
    "$2,500 - $2,999",
    "$3,000 - $3,999",
    "$4,000 - $4,999",
    "$5,000 - $5,999",
    "$6,000 - $6,999",
    "$7,000 - $7,999",
    "$8,000 - $8,999",
    "$9,000 - $9,999",
    "$10,000 - $10,999",
    "$11,000 - $11,999",
    "$12,000 & Over",
]

med_inc_bracket = []
for index, row in incdf_cs.iterrows():
    med_inc_bracket.append(row[inc_brackets].gt(row["cum_med_pop"]).idxmax())

incdf_cs["med_inc_bracket"] = med_inc_bracket

brack_mid = {
    "Below $1,000": 500,
    "$1,000 - $1,499": 1250,
    "$1,500 - $1,999": 1750,
    "$2,000 - $2,499": 2250,
    "$2,500 - $2,999": 2750,
    "$3,000 - $3,999": 3500,
    "$4,000 - $4,999": 4500,
    "$5,000 - $5,999": 5500,
    "$6,000 - $6,999": 6500,
    "$7,000 - $7,999": 7500,
    "$8,000 - $8,999": 8500,
    "$9,000 - $9,999": 9500,
    "$10,000 - $10,999": 10500,
    "$11,000 - $11,999": 11500,
    "$12,000 & Over": 12500,
}

incdf_cs["median_inc"] = incdf_cs["med_inc_bracket"].map(brack_mid)

# Merging DFs
incdf = incdf_cs[["Planning Area", "median_inc"]]
geoinc = geodf.merge(incdf, on="Planning Area", how="left")

incdf.head()

# %% [markdown]
# #### Load Flat Resale Price Data

# %%
# Flat Resale Price Data Wrangle
flat_df = pd.read_csv(
    "resale-flat-prices-based-on-registration-date-from-jan-2017-onwards.csv"
)
flat_df = flat_df[flat_df["month"] == "2021-04"]
flat_df = flat_df[["town", "resale_price"]]
flat_df = flat_df.groupby(["town"]).mean()

flat_df.reset_index(inplace=True)
flat_df.rename(columns={"town": "Planning Area"}, inplace=True)
flat_df["Planning Area"].replace({"KALLANG/WHAMPOA": "KALLANG"}, inplace=True)
flat_df["resale_price"] = flat_df["resale_price"].round(2)

geoflat = geodf.merge(flat_df, on="Planning Area", how="left")

flat_df.head()

# %% [markdown]
# ### Bubble Tea Shop Coordinates
# %% [markdown]
# #### Scraping Xing Fu Tang Addresses from Homepage

# %%
# Xing Fu Tang (Singapore) Locations
# Scraping addresses from official website
xft_get = requests.get("https://xingfutangsg.com").text
soup = BeautifulSoup(xft_get, "html.parser")
xft_add_raw = soup.find_all(class_="vc-hoverbox-block-inner vc-hoverbox-back-inner")

# Extracting addresses into list
xft_add = []
for add in xft_add_raw:
    add_temp = add.text.strip().replace("\xa0", " ")
    add_temp = add_temp.replace("\n", "|")
    add_temp = add_temp.replace("MRT", "")
    add_temp = add_temp.split("| ")
    xft_add.append(add_temp[0])

# Setting Nominatim coords into lists
xft_lat = []
xft_lng = []
for add in xft_add:
    geolocator = Nominatim(user_agent="foursquare_agent")
    location = geolocator.geocode("{} Singapore".format(add))
    xft_lat.append(location.latitude)
    xft_lng.append(location.longitude)

print(xft_add)

# %% [markdown]
# #### Foursquare API Credentials

# %%
get_ipython().run_line_magic("load_ext", "dotenv")
get_ipython().run_line_magic("dotenv", "")


# %%
# You'll need to replace with your own keys to access the Foursquare API
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# %% [markdown]
# #### API Request for Bubble Tea Locations

# %%
# Other Bubble Tea Locations in Singapore - Getting Data from Foursquare API
# Define Foursquare Credentials and Version
VERSION = "20210101"
BUBBLE_ID = "52e81612bcbc57f1066b7a0c"
AREA = "Singapore%2C%20Singapore"

# Identifying Top 9 Bubble Tea Chains in Singapore (excluding Xing Fu Tang)
# Source: http://topten.sg/food/7916
BUBBLE_CHAINS = [
    "KOI The",
    "Gong Cha",
    "Tiger Sugar",
    "Heytea",
    "PlayMade",
    "R&B Tea",
    "Sharetea",
    "Milksha",
    "LiHO",
]
LIMIT = 100

# Creating empty dataframe
fs_df = pd.DataFrame(
    columns=[
        "id",
        "name",
        "categories",
        "referralId",
        "hasPerk",
        "location.address",
        "location.crossStreet",
        "location.lat",
        "location.lng",
        "location.labeledLatLngs",
        "location.postalCode",
        "location.cc",
        "location.city",
        "location.country",
        "location.formattedAddress",
        "location.neighborhood",
        "location.state",
        "venuePage.id",
    ]
)

for chain in BUBBLE_CHAINS:
    fs_url = "https://api.foursquare.com/v2/venues/search?client_id={}&client_secret={}&near={}&oauth_token={}&v={}&query={}&categoryId={}&limit={}".format(
        CLIENT_ID, CLIENT_SECRET, AREA, ACCESS_TOKEN, VERSION, chain, BUBBLE_ID, LIMIT,
    )

    fs_results = requests.get(fs_url).json()

    # Assign relevant part of JSON to venues
    fs_venues = fs_results["response"]["venues"]

    # Tranform venues into a dataframe
    fs_df_temp = pd.json_normalize(fs_venues)

    # Append to main dataframe
    fs_df = fs_df.append(fs_df_temp, ignore_index=True)


# %%
# Filtering results from other countries
fs_df = fs_df[fs_df["location.country"].str.contains("Singapore")]

# Dropping duplicated results based on Foursquare Place ID
fs_df.drop_duplicates(subset=["id"], inplace=True)

fs_df.head()

# %% [markdown]
# ### Geospatial Visualisation
# %% [markdown]
# #### Plot of Xing Fu Tang Location vs. Locations of Other Bubble Tea Shop

# %%
# Plotting locations on Folium map
xft_map = folium.Map(
    location=[1.3521, 103.8198], tiles="cartodbpositron", zoom_start=11
)

# Plotting Planning Area borders
folium.GeoJson(
    geodf,
    name="Planning Area Borders",
    style_function=style_function,
    highlight_function=highlight_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["Planning Area"],
        aliases=["Planning Area: "],
        style=(
            "background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"
        ),
    ),
).add_to(xft_map)

# Plotting MRT Stations
# Credit: https://www.kaggle.com/yxlee245/singapore-train-station-coordinates?select=mrt_lrt_data.csv
mrt_df = pd.read_csv("mrt_lrt_data.csv")
mrt_df = mrt_df[mrt_df["type"] == "MRT"]  # Filtering out other station types

# # Plotting MRT Stations onto map
# for index, row in mrt_df.iterrows():
#     lat = row["lat"]
#     lng = row["lng"]
#     name = row["station_name"]
#     type_ = row["type"]

#     folium.CircleMarker(
#         location=[lat, lng],
#         radius=1,
#         popup="{} ({})".format(name, type_),
#         color="Grey",
#         fill_color="Grey",
#         fill_opacity=1,
#     ).add_to(xft_map)

HeatMap(mrt_df[["lat", "lng"]].values.tolist(), name="MRT Heatmap", radius=12).add_to(
    xft_map
)

# Other Bubble Tea Outlets from Foursquare API
for index, row in fs_df.iterrows():
    lat = row["location.lat"]
    lng = row["location.lng"]
    name = row["name"]

    folium.CircleMarker(
        location=[lat, lng],
        radius=3,
        weight=0,
        popup=name,
        color="Blue",
        fill_color="Blue",
        fill_opacity=0.5,
    ).add_to(xft_map)

# Adding Xing Fu Tang Location
for lat, lng, add in zip(xft_lat, xft_lng, xft_add):
    folium.CircleMarker(
        location=[lat, lng],
        radius=5,
        weight=2,
        popup="Xing Fu Tang @ {}".format(add),
        color="Black",
        fill_color="Red",
        fill_opacity=1,
    ).add_to(xft_map)

# Drawing Legend on Map
# Credit: https://github.com/python-visualization/folium/issues/528#issuecomment-421445303 (Colin Talbert)
template = """
{% macro html(this, kwargs) %}

<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>jQuery UI Draggable - Default functionality</title>
  <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

  <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
  <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
  
  <script>
  $( function() {
    $( "#maplegend" ).draggable({
                    start: function (event, ui) {
                        $(this).css({
                            right: "auto",
                            top: "auto",
                            bottom: "auto"
                        });
                    }
                });
});

  </script>
</head>
<body>

 
<div id='maplegend' class='maplegend' 
    style='position: absolute; z-index:9999; border:0px solid grey; background-color:rgba(255, 255, 255, 0.8);
     border-radius:1px; padding: 10px; font-size:12px; right: 20px; bottom: 20px;'>
     
<div class='legend-title'>Legend</div>
<div class='legend-scale'>
  <ul class='legend-labels'>
    <li><span style='background:red;opacity:0.7;'></span>Xing Fu Tang Outlets</li>
    <li><span style='background:blue;opacity:0.7;'></span>Other Bubble Tea Outlets</li>
    
  </ul>
</div>
</div>
 
</body>
</html>

<style type='text/css'>
  .maplegend .legend-title {
    text-align: left;
    margin-bottom: 5px;
    font-weight: bold;
    font-size: 90%;
    }
  .maplegend .legend-scale ul {
    margin: 0;
    margin-bottom: 5px;
    padding: 0;
    float: left;
    list-style: none;
    }
  .maplegend .legend-scale ul li {
    font-size: 80%;
    list-style: none;
    margin-left: 0;
    line-height: 18px;
    margin-bottom: 2px;
    }
  .maplegend ul.legend-labels li span {
    display: block;
    float: left;
    height: 16px;
    width: 16px;
    margin-right: 5px;
    margin-left: 0;
    border: 0px solid #999;
    }
  .maplegend .legend-source {
    font-size: 80%;
    color: #777;
    clear: both;
    }
  .maplegend a {
    color: #777;
    }
</style>
{% endmacro %}"""

macro = MacroElement()
macro._template = Template(template)

xft_map.get_root().add_child(macro)
folium.LayerControl().add_to(xft_map)
xft_map


# %%
# Flat Resale Prices + Income Bubble Map plotting
# Merging 2 dataframes into one geodataframe
geoflatinc = geoinc.merge(
    flat_df[["Planning Area", "resale_price"]], on="Planning Area", how="left"
)

flatinc_map = folium.Map(
    location=[1.3521, 103.8198], tiles="cartodbpositron", zoom_start=11
)

# Flat Resale Prices Choropleth
folium.Choropleth(
    geoflatinc,
    name="Flat Resale Prices by Planning Area (April 2021)",
    legend_name="Flat Resale Prices (as of April 2021)",
    data=geoflatinc,
    columns=["Planning Area", "resale_price"],
    key_on="feature.properties.Planning Area",
    fill_color="Greens",
    fill_opacity=1,
    line_opacity=0.2,
).add_to(flatinc_map)

# Defining Income Bubble colours
norm = Normalize(vmin=0, vmax=12500.0)  # Normalisation required
color_mapper = cm.ScalarMappable(cmap=cm.YlOrRd, norm=norm)
rgb_values = color_mapper.to_rgba(geoflatinc["median_inc"])[
    :, :3
]  # keep rgb and drop the "a" column
colors = [rgb2hex(rgb) for rgb in rgb_values]

geoflatinc["colours"] = colors
geoflatinc["colours"].replace({"#000000": np.nan}, inplace=True)

# Plot Income Bubbles
for index, row in geoflatinc.iterrows():
    lat = list(row["geometry"].centroid.coords)[0][1]
    lng = list(row["geometry"].centroid.coords)[0][0]
    colour = row["colours"]

    folium.CircleMarker(
        location=[lat, lng],
        radius=row["median_inc"] / 1200,
        color=colour,
        fill_color=colour,
        fill_opacity=1,
    ).add_to(flatinc_map)

# Tooltip plot
toolt = folium.features.GeoJson(
    geoflatinc,
    style_function=style_function,
    control=False,
    highlight_function=highlight_function,
    tooltip=folium.features.GeoJsonTooltip(
        fields=["Planning Area", "resale_price", "median_inc"],
        aliases=["Planning Area: ", "Flat Resale Price: ", "Median Income: "],
        style=(
            "background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"
        ),
    ),
)

flatinc_map.add_child(toolt)
flatinc_map.keep_in_front(toolt)

folium.LayerControl().add_to(flatinc_map)

flatinc_map


# %%
# Plotting Population and Income Map
# Merging population and income data
geopopinc = geopop.merge(
    incdf[["Planning Area", "median_inc"]], on="Planning Area", how="left"
)

# Population Map plotting
popinc_map = folium.Map(
    location=[1.3521, 103.8198], tiles="cartodbpositron", zoom_start=11
)

# Population Population Choropleth
folium.Choropleth(
    geopopinc,
    name="Population by Planning Area (2015)",
    legend_name="Population (as of 2015)",
    data=geopopinc,
    columns=["Planning Area", "Population"],
    key_on="feature.properties.Planning Area",
    fill_color="Blues",
    fill_opacity=1,
    line_opacity=0.2,
).add_to(popinc_map)

# Defining Bubble colours
norm = Normalize(vmin=0, vmax=12500.0)  # Normalisation required
color_mapper = cm.ScalarMappable(cmap=cm.YlOrRd, norm=norm)
rgb_values = color_mapper.to_rgba(geopopinc["median_inc"])[
    :, :3
]  # keep rgb and drop the "a" column
colors = [rgb2hex(rgb) for rgb in rgb_values]

geopopinc["colours"] = colors
geopopinc["colours"].replace({"#000000": np.nan}, inplace=True)

# Plot Bubbles
for index, row in geopopinc.iterrows():
    lat = list(row["geometry"].centroid.coords)[0][1]
    lng = list(row["geometry"].centroid.coords)[0][0]
    colour = row["colours"]

    folium.CircleMarker(
        location=[lat, lng],
        radius=row["median_inc"] / 1200,
        color=colour,
        fill_color=colour,
        fill_opacity=1,
    ).add_to(popinc_map)

# Tooltip plot
toolt = folium.features.GeoJson(
    geopopinc,
    style_function=style_function,
    control=False,
    highlight_function=highlight_function,
    tooltip=folium.features.GeoJsonTooltip(
        fields=["Planning Area", "Population", "median_inc"],
        aliases=["Planning Area: ", "Population: ", "Median Income: "],
        style=(
            "background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"
        ),
    ),
)

popinc_map.add_child(toolt)
popinc_map.keep_in_front(toolt)

folium.LayerControl().add_to(popinc_map)

popinc_map


# %%
# Population Map plotting
# pop_map = folium.Map(
#     location=[1.3521, 103.8198], tiles="cartodbpositron", zoom_start=10
# )

# # Population Population Choropleth
# folium.Choropleth(
#     geopop,
#     name="Population by Planning Area (2015)",
#     legend_name="Population (as of 2015)",
#     data=geopop,
#     columns=["Planning Area", "Population"],
#     key_on="feature.properties.Planning Area",
#     fill_color="YlOrRd",
#     nan_fill_color="#FFFFFF",
#     fill_opacity=0.35,
#     line_opacity=0.2,
# ).add_to(pop_map)

# toolt = folium.features.GeoJson(
#     geopop,
#     style_function=style_function,
#     control=False,
#     highlight_function=highlight_function,
#     tooltip=folium.features.GeoJsonTooltip(
#         fields=["Planning Area", "Population"],
#         aliases=["Planning Area: ", "Population: "],
#         style=(
#             "background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"
#         ),
#     ),
# )
# pop_map.add_child(toolt)
# pop_map.keep_in_front(toolt)
# folium.LayerControl().add_to(pop_map)
# pop_map

# %% [markdown]
# ## Methodology
# %% [markdown]
# ## Analysis
# %% [markdown]
# ## Results and Discussion
# %% [markdown]
# ## Conclusion
# %% [markdown]
# ## Reference

# %%


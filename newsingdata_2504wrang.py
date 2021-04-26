# %%
import os

import folium
import geopandas as gpd
import pandas as pd
import requests
from branca.element import MacroElement, Template
from bs4 import BeautifulSoup
from folium.plugins import HeatMap
from geopy.geocoders import (
    Nominatim,
)  # module to convert an address into latitude and longitude values
from IPython import get_ipython
from matplotlib import cm
from matplotlib.colors import Normalize, rgb2hex
from shapely.geometry import Point
from shapely.geometry.collection import GeometryCollection
from shapely.geometry.multipolygon import MultiPolygon

# %%
# Geodata Preparation
planarea_geo = r"MP14_PLNG_AREA_NO_SEA_PL.geojson"  # Planning Area boundaries
subzone_geo = (
    r"master-plan-2019-subzone-boundary-no-sea-kml.geojson"  # Subzone boundaries
)

# Planning Area GeoDataFrame
plan_geodata = gpd.read_file(planarea_geo)
plan_geodf = plan_geodata[["name", "id", "geometry"]]
plan_geodf = plan_geodf.rename(columns={"name": "Planning Area"})

# Converting GeometryCollection to Multipolygon to support Planning Areas with islands
plan_geodf["geometry"] = [
    MultiPolygon([feature]) if isinstance(feature, GeometryCollection) else feature
    for feature in plan_geodf["geometry"]
]  # Required or else highlight function may not work

# Subzone GeoDataFrame
sub_geodata = gpd.read_file(subzone_geo)
sub_geodf = sub_geodata[["SUBZONE_N", "PLN_AREA_N", "geometry"]]
sub_geodf = sub_geodf.rename(
    columns={"SUBZONE_N": "Subzone", "PLN_AREA_N": "Planning Area"}
)

# Converting GeometryCollection to Multipolygon to support Subzones with islands
sub_geodf["geometry"] = [
    MultiPolygon([feature]) if isinstance(feature, GeometryCollection) else feature
    for feature in sub_geodf["geometry"]
]  # Required or else highlight function may not work

# %%
# Plotting Planning Area and Subzones on Map
m = folium.Map(location=[1.3521, 103.8198], tiles="cartodbpositron", zoom_start=11)

# Map Highlight function
highlight_function = lambda x: {
    "fillColor": "#000000",
    "color": "#000000",
    "fillOpacity": 0.50,
    "weight": 0.1,
}

# Subzone Boundaries
folium.GeoJson(
    sub_geodf,
    name="Subzone Borders",
    style_function=lambda x: {
        "fillColor": "#ffffff",
        "color": "#AEDE74",
        "fillOpacity": 0.1,
        "weight": 1,
    },
    highlight_function=highlight_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["Subzone", "Planning Area"],
        aliases=["Subzone: ", "Planning Area: "],
        style=(
            "background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"
        ),
    ),
).add_to(m)

# Planning Area Boundaries
folium.GeoJson(
    plan_geodf,
    name="Planning Area Borders",
    style_function=lambda x: {
        "fillColor": "#00000000",
        "color": "#488776",
        "fill": False,
        "weight": 2,
    },
    # highlight_function=highlight_function,
    # tooltip=folium.GeoJsonTooltip(
    #     fields=["Planning Area"],
    #     aliases=["Planning Area: "],
    #     style=(
    #         "background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"
    #     ),
    # ),
).add_to(m)

m

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
# #### API Request for Bubble Tea Locations

# %%
get_ipython().run_line_magic("load_ext", "dotenv")
get_ipython().run_line_magic("dotenv", "")

# %%
# Other Bubble Tea Shop Locations
# You'll need to replace with your own keys to access the Foursquare API
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# Other Bubble Tea Locations in Singapore - Getting Data from Foursquare API
# Define Foursquare information
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
boba_df = pd.DataFrame(
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
    boba_url = "https://api.foursquare.com/v2/venues/search?client_id={}&client_secret={}&near={}&oauth_token={}&v={}&query={}&categoryId={}&limit={}".format(
        CLIENT_ID, CLIENT_SECRET, AREA, ACCESS_TOKEN, VERSION, chain, BUBBLE_ID, LIMIT,
    )

    boba_results = requests.get(boba_url).json()

    # Assign relevant part of JSON to venues
    boba_venues = boba_results["response"]["venues"]

    # Tranform venues into a dataframe
    boba_df_temp = pd.json_normalize(boba_venues)

    # Append to main dataframe
    boba_df = boba_df.append(boba_df_temp, ignore_index=True)

# Filtering results from other countries
boba_df = boba_df[boba_df["location.country"].str.contains("Singapore")]

# Dropping duplicated results based on Foursquare Place ID
boba_df.drop_duplicates(subset=["id"], inplace=True)

boba_df.head()

# %%
# Plotting Bubble Tea Outlets
# Other Bubble Tea Outlets from Foursquare API
for index, row in boba_df.iterrows():
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
    ).add_to(m)

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
    ).add_to(m)

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

m.get_root().add_child(macro)

# %%
# Plotting MRT Station Heat Map
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
#     ).add_to(m)

HeatMap(
    mrt_df[["lat", "lng"]].values.tolist(), name="MRT Heatmap", radius=12, max_zoom=13
).add_to(m)

folium.LayerControl().add_to(m)  # Adding layer controls

m

# %%
# Foursquare Shopping Malls
# Creating empty dataframe
mall_df = pd.DataFrame(
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

# Category IDs for Shopping Mall, Shopping Plaza, Outlet Mall, Outlet Store and Supermarket
MALL_ID = [
    "4bf58dd8d48988d1fd941735",
    "5744ccdfe4b0c0459246b4dc",
    "5744ccdfe4b0c0459246b4df",
    "52f2ab2ebcbc57f1066b8b35",
    "52f2ab2ebcbc57f1066b8b46",
]

for mall_ID in MALL_ID:
    mall_url = "https://api.foursquare.com/v2/venues/search?client_id={}&client_secret={}&near={}&oauth_token={}&v={}&categoryId={}&limit={}".format(
        CLIENT_ID, CLIENT_SECRET, AREA, ACCESS_TOKEN, VERSION, mall_ID, LIMIT,
    )

    mall_results = requests.get(mall_url).json()

    # Assign relevant part of JSON to venues
    mall_venues = mall_results["response"]["venues"]

    # Tranform venues into a dataframe
    mall_df_temp = pd.json_normalize(mall_venues)

    # Append to main dataframe
    mall_df = mall_df.append(mall_df_temp, ignore_index=True)

# Filtering results from other countries
mall_df = mall_df[mall_df["location.country"].str.contains("Singapore")]

# Dropping duplicated results based on Foursquare Place ID
mall_df.drop_duplicates(subset=["id"], inplace=True)

mall_df.head()

# %%
# Plotting Shopping Malls HeatMap against Bubble Tea shop locations
# Replotting Planning Area and Subzone Boundaries
m1 = folium.Map(location=[1.3521, 103.8198], tiles="cartodbpositron", zoom_start=11)

# Subzone Boundaries
folium.GeoJson(
    sub_geodf,
    name="Subzone Borders",
    style_function=lambda x: {
        "fillColor": "#ffffff",
        "color": "#AEDE74",
        "fillOpacity": 0.1,
        "weight": 1,
    },
    highlight_function=highlight_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["Subzone", "Planning Area"],
        aliases=["Subzone: ", "Planning Area: "],
        style=(
            "background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"
        ),
    ),
).add_to(m1)

# Planning Area Boundaries
folium.GeoJson(
    plan_geodf,
    name="Planning Area Borders",
    style_function=lambda x: {
        "fillColor": "#00000000",
        "color": "#488776",
        "fill": False,
        "weight": 2,
    },
).add_to(m1)

# Other Bubble Tea Outlets from Foursquare API
for index, row in boba_df.iterrows():
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
    ).add_to(m1)

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
    ).add_to(m1)

m1.get_root().add_child(macro)  # Adding legend

# Shopping Mall HeatMap
HeatMap(
    mall_df[["location.lat", "location.lng"]].values.tolist(),
    name="Shopping Mall Heatmap",
    radius=15,
    max_zoom=13,
).add_to(m1)

folium.LayerControl().add_to(m1)  # Adding layer controls

m1

# %%
# Defining Function to count points in a list in a Subzone/Planning Area (Polygon/Multipolygon)
def count_point_in_polygon(polygon, lat_list, lng_list):
    """Iterates through a list of lats and lngs and counts number of coordinates within a polygon"""
    count = []
    for latitude, longitude in zip(lng_list, lat_list):
        count.append(polygon.contains(Point(longitude, latitude)))

    return sum(count)


# %%


# %%
# Reading Data File
df = pd.read_csv("respopagesextod2011to2020.csv")
df.columns = [
    "Planning Area",
    "Subzone",
    "Age Group",
    "Sex",
    "Type of Dwelling",
    "Population",
    "Time",
]

df = df[df["Time"] == 2020]  # Only 2020 data

# Converting columns to uppercase
df["Planning Area"] = df["Planning Area"].str.upper()
df["Subzone"] = df["Subzone"].str.upper()

# %%
# https://www.mortgagesupermart.com.sg/resources/types-of-dwellings-properties

# %%
# Data needed:
# Population (20 to 44yo)
# Land Value Index based on average TOD
# Income [y]

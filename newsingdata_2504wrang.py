# %%
# Import libraries
import math
import os

import branca.colormap as cmp
import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import requests
from branca.element import MacroElement, Template
from bs4 import BeautifulSoup
from folium.plugins import HeatMap
from geopy.geocoders import (
    Nominatim,
)  # module to convert an address into latitude and longitude values
from IPython import get_ipython
from shapely.geometry import Point
from shapely.geometry.collection import GeometryCollection
from shapely.geometry.multipolygon import MultiPolygon
from sklearn.cluster import KMeans
from sklearn.impute import KNNImputer
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

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
# Map Functions
# Map Highlight function
highlight_function = lambda x: {
    "fillColor": "#000000",
    "color": "#000000",
    "fillOpacity": 0.50,
    "weight": 0.1,
}

# Subzone Style function
sub_style_function = lambda x: {
    "fillColor": "#ffffff",
    "color": "Grey",
    "fillOpacity": 0.1,
    "weight": 0.7,
}

# Planning Area Style function:
plan_style_function = lambda x: {
    "fillColor": "#00000000",
    "color": "Black",
    "fill": False,
    "weight": 1,
}

# Drawing Legend on Map
# Credit: https://github.com/python-visualization/folium/issues/528#issuecomment-421445303 (Colin Talbert)
bubble_template = """
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

bubble_macro = MacroElement()
bubble_macro._template = Template(bubble_template)

# MRT and Shopping Mall Legend
mrt_mall_template = """
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
    <li><span style='background:#00FF00;opacity:0.7;'></span>MRT Stations</li>
    <li><span style='background:#FF00FF;opacity:0.7;'></span>Shopping Malls</li>
    
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

mrt_mall_macro = MacroElement()
mrt_mall_macro._template = Template(mrt_mall_template)

# %%
# Plotting Planning Area and Subzones on Map
m = folium.Map(location=[1.3521, 103.8198], tiles="cartodbpositron", zoom_start=11)

# Subzone Boundaries
sub_border = folium.GeoJson(
    sub_geodf,
    name="Subzone Borders",
    style_function=sub_style_function,
    highlight_function=highlight_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["Subzone", "Planning Area"],
        aliases=["Subzone: ", "Planning Area: "],
        style=(
            "background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"
        ),
    ),
)

# Planning Area Boundaries
plan_border = folium.GeoJson(
    plan_geodf, name="Planning Area Borders", style_function=plan_style_function,
)

sub_border.add_to(m)
plan_border.add_to(m)

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

xft_add

# %%
# Loading Foursquare credentials
get_ipython().run_line_magic("load_ext", "dotenv")
get_ipython().run_line_magic("dotenv", "")

# You'll need to replace with your own keys to access the Foursquare API
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# %%
# Other Bubble Tea Locations in Singapore - Getting Data from Foursquare API
# Define Foursquare information
VERSION = "20210101"
BUBBLE_ID = "52e81612bcbc57f1066b7a0c"
AREA = "Singapore%2C%20Singapore"

# Identifying Top 9 Bubble Tea Chains in Singapore (excluding Xing Fu Tang)
# Source: http://topten.sg/food/7916
BUBBLE_CHAINS = [
    "KOI",
    "Gong Cha",
    "Tiger Sugar",
    "Heytea",
    "PlayMade",
    "R&B Tea",
    "Sharetea",
    "Milksha",
    "LiHO",
    "Hollin",
    "Truedan",
]
LIMIT = 200

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
    boba_url = "https://api.foursquare.com/v2/venues/search?categoryId={}&client_id={}&client_secret={}&near={}&oauth_token={}&v={}&query={}&limit={}".format(
        BUBBLE_ID, CLIENT_ID, CLIENT_SECRET, AREA, ACCESS_TOKEN, VERSION, chain, LIMIT,
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

# Filtering results that are not Bubble Tea Shops
boba_df_cat = boba_df.categories.apply(pd.Series).iloc[:, 0].apply(pd.Series)
boba_df_cat.rename(columns={"id": "cat_id", "name": "cat_name"}, inplace=True)
boba_df = boba_df.join(boba_df_cat)
boba_df = boba_df[boba_df["cat_name"] == "Bubble Tea Shop"]

# Dropping duplicated results based on Foursquare Place ID
boba_df.drop_duplicates(subset=["id"], inplace=True)
boba_df.reset_index(inplace=True, drop=True)

print(
    "Categories of venues: {}".format(boba_df["cat_name"].unique())
)  # Checking Categories
boba_df

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

m.get_root().add_child(bubble_macro)

# %%
# MRT Station Location Dataframe
# Credit: https://www.kaggle.com/yxlee245/singapore-train-station-coordinates?select=mrt_lrt_data.csv
mrt_df = pd.read_csv("mrt_lrt_data.csv")
mrt_df = mrt_df[mrt_df["type"] == "MRT"]  # Filtering out other station types

# %%
# Plotting MRT Stations Heatmap
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

# Category IDs for Shopping Mall
MALL_ID = "4bf58dd8d48988d1fd941735"

mall_url = "https://api.foursquare.com/v2/venues/search?categoryId={}&client_id={}&client_secret={}&near={}&oauth_token={}&v={}&limit={}".format(
    MALL_ID, CLIENT_ID, CLIENT_SECRET, AREA, ACCESS_TOKEN, VERSION, LIMIT,
)

mall_results = requests.get(mall_url).json()

# Assign relevant part of JSON to venues
mall_venues = mall_results["response"]["venues"]

# Tranform venues into a dataframe
mall_df = pd.json_normalize(mall_venues)

# Filtering results from other countries
mall_df = mall_df[mall_df["location.country"].str.contains("Singapore")]

# Filtering results that are not Shopping Mall, Shopping Plaza, Outlet Mall or Supermarket
mall_df_cat = mall_df.categories.apply(pd.Series).iloc[:, 0].apply(pd.Series)
mall_df_cat.rename(columns={"id": "cat_df", "name": "cat_name"}, inplace=True)
mall_df = mall_df.join(mall_df_cat)
mall_df = mall_df[
    mall_df["cat_name"].isin(["Shopping Mall", "Shopping Plaza", "Supermarket"])
]

# Dropping duplicated results based on Foursquare Place ID
mall_df.drop_duplicates(subset=["id"], inplace=True)
mall_df.reset_index(inplace=True, drop=True)

print(
    "Categories of venues: {}".format(mall_df["cat_name"].unique())
)  # Checking Categories
mall_df

# %%
# Plotting Shopping Malls HeatMap against Bubble Tea shop locations
m1 = folium.Map(location=[1.3521, 103.8198], tiles="cartodbpositron", zoom_start=11)

# Subzone Boundaries
sub_border.add_to(m1)

# Planning Area Boundaries
plan_border.add_to(m1)

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

m1.get_root().add_child(bubble_macro)  # Adding legend

# Shopping Mall HeatMap
HeatMap(
    mall_df[["location.lat", "location.lng"]].values.tolist(),
    name="Shopping Mall Heatmap",
    radius=12,
    max_zoom=13,
).add_to(m1)

folium.LayerControl().add_to(m1)  # Adding layer controls

m1

# %%
# Defining Function to count points in a list in a Subzone/Planning Area (Polygon/Multipolygon)
def count_point_in_polygon(polygon, lat_list, lng_list):
    """Iterates through a list of lats and lngs and counts number of coordinates within a polygon"""
    count = []
    for latitude, longitude in zip(lat_list, lng_list):
        count.append(polygon.contains(Point(longitude, latitude)))

    return sum(count)


# %%
# Counting all features on Subzones
# Counting number of Other Bubble Tea Stores in Subzone
for index, row in sub_geodf.iterrows():
    count_ = count_point_in_polygon(
        row["geometry"], boba_df["location.lat"], boba_df["location.lng"]
    )

    # Adding to a column in sub_geodf
    sub_geodf.loc[index, "other_boba_count"] = count_

# Counting number of Xing Fu Tang Stores in Subzone
for index, row in sub_geodf.iterrows():
    count_ = count_point_in_polygon(row["geometry"], xft_lat, xft_lng)

    # Adding to a column in sub_geodf
    sub_geodf.loc[index, "xft_boba_count"] = count_

# Counting number of MRT Stations in Subzone
for index, row in sub_geodf.iterrows():
    count_ = count_point_in_polygon(row["geometry"], mrt_df["lat"], mrt_df["lng"])

    # Adding to a column in sub_geodf
    sub_geodf.loc[index, "mrt_count"] = count_

# Counting number of Shopping Malls in Subzone
for index, row in sub_geodf.iterrows():
    count_ = count_point_in_polygon(
        row["geometry"], mall_df["location.lat"], mall_df["location.lng"]
    )

    # Adding to a column in sub_geodf
    sub_geodf.loc[index, "mall_count"] = count_

# %%
# Reading Population/Age and Dwelling Type Data File (Previously trimmed to only include 2020 data)
pt_df = pd.read_csv("respopagesextod2020.csv")
pt_df.columns = [
    "Planning Area",
    "Subzone",
    "Age Group",
    "Sex",
    "Type of Dwelling",
    "Population",
    "Time",
]

# Converting columns to uppercase
pt_df["Planning Area"] = pt_df["Planning Area"].str.upper()
pt_df["Subzone"] = pt_df["Subzone"].str.upper()

# %%
# # Calculating Population by Age Group by Subzone
# # NOTE Potential for performance improvements
# age_ranges = list(pt_df["Age Group"].unique())
# age_df = pd.DataFrame(sz_list, columns=["Subzone"])
# pt_trim_df = pt_df[["Subzone", "Age Group", "Population"]]

# for age in age_ranges:
#     age_list = []
#     for subzone in sz_list:
#         age_sum = pt_trim_df.loc[(pt_trim_df["Subzone"] == subzone) & (pt_trim_df["Age Group"] == age)]["Population"].sum()
#         age_list.append((subzone, age_sum))
#     age_df = age_df.merge(
#         pd.DataFrame(age_list, columns=["Subzone", age]), how="left", on="Subzone"
#     )

# # Getting total population of target age group
# age_df["pop_total20_44"] = age_df[['20_to_24','25_to_29', '30_to_34', '35_to_39', '40_to_44']].sum(axis=1)
# age_df.to_csv("ages_pop2020.csv", index=False)

age_df = pd.read_csv("ages_pop2020.csv")

# %%
# Setting Type of Dwelling into Dwelling Index
# https://www.mortgagesupermart.com.sg/resources/types-of-dwellings-properties
tod_key = list(pt_df["Type of Dwelling"].unique())  # list of dwelling types
tod_val = [2, 3, 4, 5, 6, 8, 7, 1]  # Giving weights to TOD
tod_dict = {tod_key[i]: tod_val[i] for i in range(len(tod_key))}
tod_dict

pt_df["Dwelling Weight"] = pt_df["Type of Dwelling"].map(tod_dict)
pt_df["Dwelling Index"] = pt_df["Dwelling Weight"] * pt_df["Population"]
pt_df.head()

sz_list = list(pt_df["Subzone"].unique())  # List of subzones

# Setting Sum of Population and Dwelling Index into a DataFrame
dwell_list = []
pop_list = []

for subzone in sz_list:
    index_sum = pt_df.loc[pt_df["Subzone"] == subzone]["Dwelling Index"].sum()
    pop_sum = pt_df.loc[pt_df["Subzone"] == subzone]["Population"].sum()
    count_ = index_sum / pop_sum
    dwell_list.append((subzone, count_))
    pop_list.append((subzone, pop_sum))

dwell_df = pd.DataFrame(dwell_list, columns=["Subzone", "Dwelling Index"])
pop_df = pd.DataFrame(pop_list, columns=["Subzone", "Population"])

# Merging Dwelling Index into Subzone GeoDataFrame
sub_geodf = pd.merge(sub_geodf, dwell_df, how="left", on="Subzone")
sub_geodf = pd.merge(sub_geodf, pop_df, how="left", on="Subzone")

# Renaming columns for consistency
sub_geodf.rename(
    columns={"Dwelling Index": "dwell_idx", "Population": "pop_total"}, inplace=True
)

# Merging ages DataFrame with geoDataFrame
# main_geodf = sub_geodf.merge(age_df, how="left", on="Subzone")
main_geodf = sub_geodf.merge(
    age_df[["Subzone", "pop_total20_44"]], how="left", on="Subzone"
)

# %%
# Plotting Population (25yo - 45yo) Data
m2 = folium.Map(location=[1.3521, 103.8198], tiles="cartodbpositron", zoom_start=11)

# Population Choropleth
folium.Choropleth(
    main_geodf,
    name="Population",
    legend_name="Population, 2020",
    data=main_geodf,
    columns=["Subzone", "pop_total20_44"],
    key_on="feature.properties.Subzone",
    fill_color="Blues",
    fill_opacity=0.7,
    line_opacity=0.2,
).add_to(m2)

# Subzone Boundaries
folium.GeoJson(
    main_geodf,
    name="Subzone Borders",
    style_function=sub_style_function,
    highlight_function=highlight_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["Subzone", "Planning Area", "pop_total20_44"],
        aliases=["Subzone: ", "Planning Area: ", "Population (25yo - 45yo): "],
        style=(
            "background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"
        ),
    ),
).add_to(m2)

# Planning Area Boundaries
plan_border.add_to(m2)

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
    ).add_to(m2)

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
    ).add_to(m2)

m2.get_root().add_child(bubble_macro)  # Adding legend

m2
# %%
# Plotting Dwelling Type
m3 = folium.Map(location=[1.3521, 103.8198], tiles="cartodbpositron", zoom_start=11)

# Dwelling Type Choropleth
folium.Choropleth(
    main_geodf,
    name="Average Dwelling Types",
    legend_name="Dwelling Index",
    data=main_geodf,
    columns=["Subzone", "dwell_idx"],
    key_on="feature.properties.Subzone",
    fill_color="Greens",
    fill_opacity=0.7,
    line_opacity=0.2,
).add_to(m3)

# Subzone Boundaries
folium.GeoJson(
    main_geodf,
    name="Subzone Borders",
    style_function=sub_style_function,
    highlight_function=highlight_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["Subzone", "Planning Area", "dwell_idx"],
        aliases=["Subzone: ", "Planning Area: ", "Dwelling Index: "],
        style=(
            "background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"
        ),
    ),
).add_to(m3)

# Planning Area Boundaries
plan_border.add_to(m3)

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
    ).add_to(m3)

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
    ).add_to(m3)

m3.get_root().add_child(bubble_macro)  # Adding legend

m3

# %%
# Income Data Preparation
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

incdf = incdf_cs[["Planning Area", "median_inc"]]
geoinc = plan_geodf.merge(incdf, on="Planning Area", how="left")

# Set median income into main_geodf
main_geodf = main_geodf.merge(incdf, on="Planning Area", how="left")

# %%
# Plotting Income Levels
m4 = folium.Map(location=[1.3521, 103.8198], tiles="cartodbpositron", zoom_start=11)

# Income Levels Choropleth
folium.Choropleth(
    geoinc,
    name="Median Income by Planning Area",
    legend_name="Median Income (SGD)",
    data=geoinc,
    columns=["Planning Area", "median_inc"],
    key_on="feature.properties.Planning Area",
    fill_color="Purples",
    fill_opacity=0.7,
    line_opacity=0.2,
).add_to(m4)

# Planning Area Boundaries
folium.GeoJson(
    geoinc,
    name="Planning Area Borders",
    style_function=lambda x: {
        "fillColor": "#00000000",
        "color": "Black",
        "fill": True,
        "weight": 1,
    },
    highlight_function=highlight_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["Planning Area", "median_inc"],
        aliases=["Planning Area: ", "Median Income (SGD): "],
        style=(
            "background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"
        ),
    ),
).add_to(m4)

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
    ).add_to(m4)

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
    ).add_to(m4)

m4.get_root().add_child(bubble_macro)  # Adding legend

m4

# %%
# Preparing Data for Analysis
# Separating data info and data values
info_cols = ["Subzone", "Planning Area", "geometry"]
info_cols_pop = info_cols + [
    "pop_total"
]  # Removing pop_total to avoid multicollinearity with pop_total20_44
cluster_info = main_geodf[info_cols_pop]
cluster_val = main_geodf.drop(columns=info_cols)

# %%
# Example of NaN rows
cluster_val.head(2)

# %%
# Cleaning up NaN Values in dataframe
# For rows with only 0 or NaN cells
# We replace NaN with 0
for index, row in cluster_val.iterrows():
    if row.sum() == 0:
        row.fillna(0, inplace=True)
        cluster_val.loc[index] = row  # Write rows into Dataframe
    else:
        pass

# For rows that have data other than 0 for all columns
# Ww use K-nearest neighbour algorithm to estimate and fill NaNs
imputer = KNNImputer(n_neighbors=5)
filled_array = imputer.fit_transform(cluster_val)
cluster_val = pd.DataFrame(filled_array, columns=list(cluster_val.columns))
print("Anymore NaN values? {}".format(cluster_val.isnull().values.any()))

# %%
# Using StandardScaler on cluster_val
cluster_std = StandardScaler().fit_transform(cluster_val)
cluster_std

# %%
# Evaluating K-means to choose K value
kmin = 4
kmax = 13
k_list = list(range(kmin, kmax + 1))
elb = []
sil = []

for k in k_list:
    km = KMeans(n_clusters=k, random_state=0)
    km.fit(cluster_std)
    elb.append(km.inertia_)
    sil.append(silhouette_score(cluster_std, km.labels_))

# %%
# Plotting Sum of square distance and Silhouette score
fig, ax1 = plt.subplots()

ax2 = ax1.twinx()
ax1.plot(k_list, elb, "bo-")
ax2.plot(k_list, sil, "ro-")

ax1.set_xlabel("Number of clusters, k")
ax1.set_ylabel("Sum of squared distance", color="b")
ax2.set_ylabel("Silhouette score", color="r")

plt.show()

k_opt = sil.index(max(sil)) + kmin

print("Optimal k value: {}".format(k_opt))

# %%
# Run K-means clustering again with optimal k
kmeans = KMeans(n_clusters=k_opt, random_state=0).fit(cluster_std)

# Set K-means cluster labels into Dataframe (+1 to start from 1)
cluster_val["cluster"] = kmeans.labels_ + 1

# Rejoin info and value (filled) dataframes
cluster_df = cluster_info.join(cluster_val)

# Converting cluster_df into a GeoDataFrame
cluster_geodf = gpd.GeoDataFrame(cluster_df, geometry="geometry")

# %%
# Colour map for Clusters
color_list = [
    "#D3D3D3",
    "#808080",
    "#a6cee3",
    "#1f78b4",
    "#b2df8a",
    "#33a02c",
    "#fb9a99",
    "#e31a1c",
    "#fdbf6f",
    "#ff7f00",
    "#cab2d6",
    "#6a3d9a",
    "#ffff99",
    "#b15928",
    "#FFFFFF",
    "#000000",
]

# Trim colour list to number of clusters
if k_opt <= len(color_list):
    color_list = color_list[:k_opt]
else:
    print(
        "Warn: Number of clusters ({}) is larger than colours available ({})".format(
            k_opt, len(color_list)
        )
    )  # Warning won't trigger so long kmax <= color_list

color_step = cmp.StepColormap(color_list, vmin=1, vmax=k_opt, caption="Clusters",)

cluster_dict = cluster_geodf.set_index("Subzone")["cluster"]

# %%
# Plot Subzones clusters on Map
m5 = folium.Map(location=[1.3521, 103.8198], tiles="cartodbpositron", zoom_start=11)

# Colouring Subzones based on Clusters
cluster_gj = folium.GeoJson(
    cluster_geodf,
    style_function=lambda feature: {
        "fillColor": color_step(cluster_dict[feature["properties"]["Subzone"]]),
        "color": color_step(cluster_dict[feature["properties"]["Subzone"]]),
        "fillOpacity": 0.5,
        "weight": 1,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["Planning Area", "Subzone", "cluster"],
        aliases=["Planning Area: ", "Subzone: ", "Cluster: "],
        style=(
            "background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"
        ),
    ),
)

cluster_gj.add_to(m5)
plan_border.add_to(m5)
color_step.add_to(m5)

m5

# %%
# Plot Bubble Tea locations
# Other Bubble Tea Outlets from Foursquare API
m6 = folium.Map(location=[1.3521, 103.8198], tiles="cartodbpositron", zoom_start=11)

cluster_gj.add_to(m6)
plan_border.add_to(m6)
color_step.add_to(m6)

for index, row in boba_df.iterrows():
    lat = row["location.lat"]
    lng = row["location.lng"]
    name = row["name"]

    folium.CircleMarker(
        location=[lat, lng],
        radius=3,
        weight=0,
        popup=name,
        color="Black",
        fill_color="Blue",
        fill_opacity=0.5,
    ).add_to(m6)

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
    ).add_to(m6)

m6.get_root().add_child(bubble_macro)  # Adding legend

m6
# %%
# Plot MRT and Shopping Mall Location
m7 = folium.Map(location=[1.3521, 103.8198], tiles="cartodbpositron", zoom_start=11)

cluster_gj.add_to(m7)
plan_border.add_to(m7)
color_step.add_to(m7)

# MRT Locations
for index, row in mrt_df.iterrows():
    lat = row["lat"]
    lng = row["lng"]
    name = row["station_name"]

    folium.CircleMarker(
        location=[lat, lng],
        radius=3,
        weight=1,
        popup=name,
        color="black",
        fill_color="#00FF00",
        fill_opacity=1,
    ).add_to(m7)

# Shopping Mall locations from Foursquare API
for index, row in mall_df.iterrows():
    lat = row["location.lat"]
    lng = row["location.lng"]
    name = row["name"]

    folium.CircleMarker(
        location=[lat, lng],
        radius=3,
        weight=1,
        popup=name,
        color="Black",
        fill_color="#FF00FF",
        fill_opacity=1,
    ).add_to(m7)

m7.get_root().add_child(mrt_mall_macro)  # Adding legend

m7
# %%
# Scoring each feature to get cluster score
# MRT/Mall weighted scoring
bt_per_mrt = int(input("Enter your estimate of # of Bubble Tea Shop per MRT Station: "))
bt_per_mall = int(
    input("Enter your estimate of # of Bubble Tea Shop per Shopping Mall: ")
)

cluster_geodf["mrt_mall_score"] = (
    cluster_geodf["mrt_count"] * bt_per_mrt + cluster_geodf["mall_count"] * bt_per_mall
)

# Bubbled Tea Shop weighted scoring
cluster_geodf["bubble_score"] = (
    cluster_geodf["other_boba_count"] + cluster_geodf["xft_boba_count"] * 10
)

# Subzone total weighted scoring
cluster_geodf["subzone_score"] = (
    cluster_geodf["mrt_mall_score"] - cluster_geodf["bubble_score"]
)

cluster_geodf.head()

# %%
# Getting cluster group with highest subzone_score
results_df = cluster_geodf.drop(columns=info_cols)
results_df = results_df.groupby(["cluster"]).mean()
results_df = results_df.sort_values(by="subzone_score", ascending=False)
top_cluster = results_df.index[0]
print(
    "Cluster {} has the highest subzone score of {:.2f}".format(
        top_cluster, results_df.loc[top_cluster, "subzone_score"]
    )
)
results_df.head(k_opt)  # Show all clusters

# %%
# EDA of results_df
top_cluster_df = cluster_geodf[cluster_geodf["cluster"] == top_cluster].drop(
    columns=info_cols
)
top_cluster_df.describe()

# %%
# Credit: https://github.com/kyokin78/Coursera_Capstone/blob/project/CapstoneProject_OpenCinemaInMontreal.ipynb
def draw_barchart(dataframe, highlight_index):
    fig = plt.figure(figsize=(18, 15))
    n_rows = n_cols = math.ceil(math.sqrt(dataframe.columns.size))
    for i, col in enumerate(dataframe.columns):
        df = dataframe[[col]].sort_values(by=col)
        ax = fig.add_subplot(n_rows, n_cols, i + 1)
        df.plot.barh(ax=ax)
        pos = df.index.get_loc(highlight_index)
        ax.patches[pos].set_facecolor("#aa3333")
        ax.set_title(col)
        ax.get_legend().remove()
    # fig.tight_layout()
    plt.show()


draw_barchart(
    results_df[
        "pop_total20_44",
        "median_inc",
        "dwell_idx",
        "mrt_count",
        "mall_count",
        "other_boba_count",
        "xft_boba_count",
    ],
    top_cluster,
)


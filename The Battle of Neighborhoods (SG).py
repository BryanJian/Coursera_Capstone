# %%
import folium
import pandas as pd
import geopandas as gpd
from shapely.geometry.collection import GeometryCollection
from shapely.geometry.multipolygon import MultiPolygon

import random
from shapely.geometry import Point

# %%
sing_geo = r"MP14_PLNG_AREA_NO_SEA_PL.geojson"  # Geodata

# Population Data
popsheet = pd.read_excel(
    "t1-9.xls", sheet_name="T7(Total)"
)  # Read Planning Area population

# Dropping empty rows
popdf = popsheet.dropna(how="all", thresh=2)
popdf = popdf.dropna(how="all", thresh=2, axis=1)

# Making header
popdf.columns = popdf.iloc[0]
popdf = popdf[1:]

# Removing redundant headers, columns and rows
popdf = popdf[popdf["Planning Area"] != "Planning Area"]
popdf.dropna(inplace=True)
popdf = popdf[["Planning Area", "Total"]]
popdf = popdf[~popdf["Planning Area"].str.contains("Total")]

# Convert Planning Area Names to all-caps
popdf["Planning Area"] = popdf["Planning Area"].str.upper()
popdf = popdf.rename(columns={"Total": "Population"})

popdf.replace({"-": 0}, inplace=True)
popdf = popdf.reset_index(drop=True)

# GeoDataFrame
geodf = gpd.read_file(sing_geo)
geodf = geodf[["id", "name", "geometry"]]
geodf = geodf.rename(columns={"name": "Planning Area"})

# Conversion of GeometryCollection to Multipolygon to support island on map
geodf["geometry"] = [
    MultiPolygon([feature]) if isinstance(feature, GeometryCollection) else feature
    for feature in geodf["geometry"]
]

# Merging DFs
geopop = geodf.merge(popdf, on="Planning Area")

popdf.to_csv("SG_planningarea_pop.csv", index=False)
geopop.to_csv("SG_planningarea_geopop.csv", index=False)

# %%
# Tooltip style functions
style_function = lambda x: {
    "fillColor": "#ffffff",
    "color": "#000000",
    "fillOpacity": 0.1,
    "weight": 0.1,
}
highlight_function = lambda x: {
    "fillColor": "#000000",
    "color": "#000000",
    "fillOpacity": 0.50,
    "weight": 0.1,
}

# %%
# Population Map plotting
pop_map = folium.Map(
    location=[1.3521, 103.8198], tiles="cartodbpositron", zoom_start=10
)

# Population Population Choropleth
folium.Choropleth(
    geopop,
    name="Population by Planning Area (2015)",
    legend_name="Population (as of 2015)",
    data=geopop,
    columns=["Planning Area", "Population"],
    key_on="feature.properties.Planning Area",
    fill_color="YlOrRd",
    nan_fill_color="#FFFFFF",
    fill_opacity=0.35,
    line_opacity=0.2,
).add_to(pop_map)

toolt = folium.features.GeoJson(
    geopop,
    style_function=style_function,
    control=False,
    highlight_function=highlight_function,
    tooltip=folium.features.GeoJsonTooltip(
        fields=["Planning Area", "Population"],
        aliases=["Planning Area: ", "Population: "],
        style=(
            "background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"
        ),
    ),
)
pop_map.add_child(toolt)
pop_map.keep_in_front(toolt)
folium.LayerControl().add_to(pop_map)
pop_map

# %%
# Income Data
incsheet = pd.read_excel("t143-147.xls", sheet_name="T145")  # Read Planning Area income

# Dropping empty columns and rows
incdf = incsheet.dropna(how="all", thresh=3)
incdf = incdf.dropna(axis=1)

# Making Header
incdf.columns = incdf.iloc[0]
incdf = incdf[1:]

incdf = incdf[~incdf["Planning Area"].str.contains("Total")]
incdf = incdf[~incdf["Planning Area"].str.contains("Others")]
incdf = incdf.drop(columns="Total")

incdf["Planning Area"] = incdf["Planning Area"].str.upper()

incdf = incdf.reset_index(drop=True)

incdf.to_csv("SG_planningarea_inc.csv", index=False)

# %%
# Merging DFs
geoinc = geodf.merge(incdf, on="Planning Area")
geoinc.to_csv("SG_planningarea_geoinc.csv", index=False)

# %%
def generate_random(number, polygon):
    points = []
    minx, miny, maxx, maxy = polygon.bounds
    while len(points) < number:
        pnt = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if polygon.contains(pnt):
            points.append(pnt)
    return points


# %%
testpoints = generate_random(50, polygon=geopop["geometry"][1])

testmap = folium.Map(
    location=[1.3521, 103.8198], tiles="cartodbpositron", zoom_start=11
)

folium.GeoJson(
    geopop["geometry"],
    style_function=lambda x: {
        "fillColor": "#ffffff",
        "color": "#000000",
        "fillOpacity": 0,
        "weight": 1,
    },
).add_to(testmap)

for i, point_i in enumerate(testpoints, 0):
    folium.CircleMarker(
        [tuple(point_i.coords)[0][1], tuple(point_i.coords)[0][0]],
        radius=1,
        color="Blue",
        opacity=0.5,
        fill=False,
    ).add_to(testmap)

testmap
# %%
def plot_pop_points(map_obj, number, polygon, color):
    """Generates random point objects for a polygon and plots them onto a Folium map."""
    points = []
    minx, miny, maxx, maxy = polygon.bounds
    while len(points) < number:
        pnt = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if polygon.contains(pnt):
            points.append(pnt)

    for i, point_i in enumerate(points, 0):
        folium.CircleMarker(
            [tuple(point_i.coords)[0][1], tuple(point_i.coords)[0][0]],
            radius=1,
            color=color,
            opacity=0.5,
            fill=False,
        ).add_to(map_obj)


# %%
incmap = folium.Map(location=[1.3521, 103.8198], tiles="cartodbpositron", zoom_start=11)

folium.GeoJson(
    geoinc["geometry"],
    style_function=lambda x: {
        "fillColor": "#ffffff",
        "color": "#000000",
        "fillOpacity": 0,
        "weight": 1,
    },
).add_to(incmap)

folium.features.GeoJson(
    geoinc,
    style_function=style_function,
    control=False,
    highlight_function=highlight_function,
    tooltip=folium.features.GeoJsonTooltip(
        fields=["Planning Area"],
        aliases=["Planning Area: "],
        style=(
            "background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"
        ),
    ),
).add_to(incmap)

geoinc_lvl = geoinc.drop(columns=["id", "Planning Area", "geometry"])

for poly_i in geoinc["geometry"]:
    for _ in range(geoinc_lvl.shape[1]):
        plot_pop_points(incmap, 10, poly_i, "Blue")

incmap
# %%

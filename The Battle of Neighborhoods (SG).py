# %%
import folium
import pandas as pd
import numpy as np
from matplotlib import cm
from matplotlib.colors import rgb2hex
from matplotlib.colors import Normalize
import geopandas as gpd
from shapely.geometry.collection import GeometryCollection
from shapely.geometry.multipolygon import MultiPolygon

# Geodata Wrangle
sing_geo = r"MP14_PLNG_AREA_NO_SEA_PL.geojson"  # Geodata

# GeoDataFrame
geodf = gpd.read_file(sing_geo)
geodf = geodf[["name", "id", "geometry"]]
geodf = geodf.rename(columns={"name": "Planning Area"})

# Conversion of GeometryCollection to Multipolygon to support PAs with islands
geodf["geometry"] = [
    MultiPolygon([feature]) if isinstance(feature, GeometryCollection) else feature
    for feature in geodf["geometry"]
]

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
# Population Data Wrangle
popdf = pd.read_csv("SG_planningarea_pop.csv")  # Population data
# Merging DFs and saving
geopop = geodf.merge(popdf, on="Planning Area")
geopop.to_csv("SG_planningarea_geopop.csv", index=False)

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
geoinc.to_csv("SG_planningarea_geoinc_cs.csv", index=False)

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

# %%

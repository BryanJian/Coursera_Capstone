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
 incdf_prep = incdf.rename(columns=brack_dict_r)
 
brack_dict = {
0: "Below $1,000",
1: "$1,000 - $1,499",
2: "$1,500 - $1,999",
3: "$2,000 - $2,499",
4: "$2,500 - $2,999",
5: "$3,000 - $3,999",
6: "$4,000 - $4,999",
7: "$5,000 - $5,999",
8: "$6,000 - $6,999",
9: "$7,000 - $7,999",
10: "$8,000 - $8,999",
11: "$9,000 - $9,999",
12: "$10,000 - $10,999",
13: "$11,000 - $11,999",
14: "$12,000 & Over",
}

brack_dict_r = {value : key for (key, value) in brack_dict.items()}


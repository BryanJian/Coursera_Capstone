# %%
import random  # library for random number generation

import folium  # plotting library
import numpy as np  # library to handle data in a vectorized manner
import pandas as pd  # library for data analsysis
import requests  # library to handle requests
from bs4 import BeautifulSoup
from geopy.geocoders import (
    Nominatim,
)  # module to convert an address into latitude and longitude values
from IPython.core.display import HTML

# libraries for displaying images
from IPython.display import Image

print("Libraries imported.")

# %%
# Define Foursquare Credentials and Version
CLIENT_ID = "1XU00CVEYIW5RENPYBEZ02JGVHSXTHNMDMXDL04FQY41XV0ZXJRPVIN5Z5BIDOHDKZSAJYEM2IF2DDJZJV0ZH0RUABN4ERGB"  # your Foursquare ID
CLIENT_SECRET = (
    "XJRPVIN5Z5BIDOHDKZSAJYEM2IF2DDJZJV0ZH0RUABN4ERGB"  # your Foursquare Secret
)
ACCESS_TOKEN = (
    "O32LUBYDOOUMK2V4R4RQWW5IFL4YPM35SZTWJOITJZLV0SRB"  # your FourSquare Access Token
)
VERSION = "20210421"
# LIMIT = 30
print("Your credentials:")
print("CLIENT_ID: " + CLIENT_ID)
print("CLIENT_SECRET:" + CLIENT_SECRET)
# %%
# Xing Fu Tang (Singapore) Locations
xft_get = requests.get("https://xingfutangsg.com").text
soup = BeautifulSoup(xft_get, "html.parser")
xft_add = soup.find_all(class_="vc-hoverbox-block-inner vc-hoverbox-back-inner")

add_list = []
for add in xft_add:
    add_temp = add.text.strip().replace("\xa0", " ")
    add_temp = add_temp.replace("\n", "|")
    add_temp = add_temp.replace("MRT", "")
    add_temp = add_temp.split("| ")
    add_list.append(add_temp[0])
add_list
# %%
# Geopy: Xing Fu Tang

xft_lat = []
xft_lng = []
for add in add_list:
    geolocator = Nominatim(user_agent="foursquare_agent")
    location = geolocator.geocode("{} Singapore".format(add))
    xft_lat.append(location.latitude)
    xft_lng.append(location.longitude)

# %%

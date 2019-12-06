# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.3.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import os

import folium
import geopandas as gpd

from urban_technologies_berlin.utils import style_function_factory

# %%
data = "../data"
data_interim = os.path.join(data, "interim")
data_preprocessed = os.path.join(data, "preprocessed")

map_htmls = os.path.join("../reports/figures/maps/html")

# %%
# first, setup all directories
for directory in [
    map_htmls
        ]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# %%
sealing = os.path.join(data_interim, "sealing", "sealing.geojson")
district = os.path.join(data_interim, "district", "district.geojson")
ground_level = os.path.join(data_interim, "ground_level", "ground_level_subset.geojson")

df_sealing = gpd.read_file(sealing)
df_district = gpd.read_file(district)
df_ground_level = gpd.read_file(ground_level)

# %% [markdown]
# # Visualize the Data

# %%
map_district = folium.Map(location=[52.5112, 13.3965], zoom_start=12, tiles="stamentoner")
folium.GeoJson(df_district).add_to(map_district)

map_district.save(os.path.join(map_htmls, "district.html"))

# %% [markdown]
# ![District Data](../reports/figures/maps/png/district.png)

# %%
min_ground_level = df_ground_level["height"].min()
max_ground_level = df_ground_level["height"].max()

map_ground_level = folium.Map(location=[52.5112, 13.3965], zoom_start=14, tiles="stamentoner")
folium.GeoJson(df_ground_level,
                style_function=style_function_factory("height", "green", "red", (min_ground_level, max_ground_level))
              ).add_to(map_ground_level)

map_ground_level.save(os.path.join(map_htmls, "ground_level_subset.html"))

# %% [markdown]
# ![Ground Level Data](../reports/figures/maps/png/ground_level_subset.png)

# %%
map_sealing = folium.Map(location=[52.5112, 13.3965], zoom_start=12, tiles="stamentoner")
folium.GeoJson(df_sealing,
                style_function=style_function_factory("sealing", "green", "red", (0, 100))
              ).add_to(map_sealing)

map_sealing.save(os.path.join(map_htmls, "sealing.html"))

# %% [markdown]
# ![District Data](../reports/figures/maps/png/sealing.png)

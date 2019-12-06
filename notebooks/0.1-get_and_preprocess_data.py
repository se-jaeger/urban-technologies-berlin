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
import shutil
from functools import reduce
from glob import glob

import geopandas as gpd
import numpy as np

# %% [markdown]
# ## Constant Definition

# %%
data_raw = "../data/raw"

sealing_raw = os.path.join(data_raw, "sealing")
district_raw = os.path.join(data_raw, "district")
ground_level_raw = os.path.join(data_raw, "ground_level")

data_interim = "../data/interim"
sealing_interim = os.path.join(data_interim, "sealing")
district_interim = os.path.join(data_interim, "district")
ground_level_interim = os.path.join(data_interim, "ground_level")

district_url = "https://opendata.arcgis.com/datasets/9f5d82911d4545c4be1da8cab89f21ae_0.geojson"

# %%
x_coordinate_start = 390
y_coordinate_start = 5818

number_of_tiles = 2

# %%
# first, setup all directories
for directory in [
    sealing_raw,
    district_raw,
    ground_level_raw,
    sealing_interim,
    district_interim,
    ground_level_interim
        ]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# %% [markdown]
# # Ground Level of Berlin
#
# Uses the `berlin-opendata-downloader`: https://github.com/se-jaeger/berlin-gelaendemodelle-downloader
# Compress the data on the fly to a tile size of `5x5`.

# %%
# !pip install berlin-opendata-downloader
# !berlin_downloader download {ground_level_raw} --compress 5 --file-format geojson

# %%
# move the downloaded files to a more appropriate directory
files = glob(os.path.join(ground_level_raw, "compressed", "geojson", "*"))

for file in files:
    shutil.move(file, ground_level_raw)

# delete empty directories
shutil.rmtree(os.path.join(ground_level_raw, "compressed"))

# %% [markdown]
# Computing gradients on each tile separately creates errors on the borders of the tiles but would be necessary,
# if the whole data shall be use because the current approach assumes the input of gradient computing is rectangular.
# Use a subset of the data because it is
# 1. easier to use because of the dataset size
# 2. more accurate

# %%
file_names = []

for x_offset in range(number_of_tiles):
    for y_offset in range(number_of_tiles):

        x = x_coordinate_start + x_offset * 2
        y = y_coordinate_start + y_offset * 2

        file_names.append(os.path.join(ground_level_raw, f"{x}_{y}.geojson"))

# %%
# read the subset of tiles and create one Data Frame
data_frames_ground_level = [gpd.read_file(file) for file in file_names]

df_ground_level_subset = reduce(lambda a, b: a.append(b), data_frames_ground_level)

# %%
# some column selection
df_ground_level_subset.drop(columns=["x", "y"], inplace=True)

# compute gradients of the ground levels
x_size = y_size = int(np.sqrt(df_ground_level_subset.shape[0]))
ground_level_matrix = np.array(df_ground_level_subset["height"]).reshape((x_size, y_size))
ground_level_gradients = np.gradient(ground_level_matrix)

df_ground_level_subset["y gradient"] = ground_level_gradients[0].flatten()
df_ground_level_subset["x gradient"] = ground_level_gradients[1].flatten()

# %%
# save the preprocessed DataFrame
df_ground_level_subset.to_file(os.path.join(ground_level_interim, "ground_level_subset.geojson"), driver="GeoJSON")

# %%
df_ground_level_subset.head()

# %% [markdown]
# ## Ground Level Data Description
#
# TODO

# %% [markdown]
# # Districts of Berlin

# %%
# get and save the raw data
df_district = gpd.read_file(district_url)
df_district.to_crs(crs={"init": "epsg:25833"}, inplace=True)
df_district.to_file(os.path.join(district_raw, "district.geojson"), driver="GeoJSON")

# %%
# drop some columns, rename the rest, and save the data
df_district = df_district[["Gemeinde_n", "geometry"]]
df_district.columns = ["district", "geometry"]
df_district.to_file(os.path.join(district_interim, "district.geojson"), driver="GeoJSON")

# %%
df_district.head()

# %% [markdown]
# ## District Data Description
#
# TODO

# %% [markdown]
# # Level of Sealing
#
# Used the software [QGIS](https://www.qgis.org/en/site/) to download
# the data `geojson` dump to `../data/raw/sealing/sealing.geojson`.
#
# - The original map: https://fbinter.stadt-berlin.de/fb/index.jsp?loginkey=showMap&mapId=wmsk01_02versieg2016@senstadt
# - WFS: https://fbinter.stadt-berlin.de/fb/berlin/service_intern.jsp?id=sach_nutz2015_nutzsa@senstadt&type=WFS

# %%
df_sealing = gpd.read_file(os.path.join(sealing_raw, "sealing.geojson"))

# %%
df_sealing = df_sealing[["BEZIRK", "VG_0", "geometry"]]
df_sealing.columns = ["district", "sealing", "geometry"]

df_sealing.to_file(os.path.join(sealing_interim, "sealing.geojson"), driver="GeoJSON")

# %%
df_sealing.head()

# %% [markdown]
# ## Level of Sealing Data Description
#
# TODO

# %%

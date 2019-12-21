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

import contextily as ctx
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# %%
data = "../data"
data_interim = os.path.join(data, "interim")
data_preprocessed = os.path.join(data, "preprocessed")

map_pdf = os.path.join("../reports/figures/maps/pdf")

# %%
# first, setup all directories
for directory in [
    map_pdf
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
#
# ## Districts of Berlin

# %%
map_district = df_district.to_crs(epsg=3857).plot(
    figsize=(15, 15),
    alpha=0.2,
    edgecolor="black",
    linewidth=3,
)
ctx.add_basemap(map_district, url=ctx.providers.Stamen.TonerLite)
map_district.set_axis_off()

# %% [markdown]
# ## Ground Level of Berlin

# %%
min_ground_level = df_ground_level["height"].min()
max_ground_level = df_ground_level["height"].max()

map_ground_level = df_ground_level.to_crs(epsg=3857).plot(
    figsize=(15, 15),
    column="height",
    alpha=0.5,
    cmap=LinearSegmentedColormap.from_list("", ["blue", "yellow", "orange"], N=1000),
    norm=plt.Normalize(min_ground_level, max_ground_level)
)
ctx.add_basemap(map_ground_level, url=ctx.providers.Stamen.TonerLite)
map_ground_level.set_axis_off()

# %% [markdown]
# ## Level of Sealing of Berlin

# %%
map_sealing = df_sealing.to_crs(epsg=3857).plot(
    figsize=(15, 15),
    column="sealing",
    alpha=0.5,
    cmap=LinearSegmentedColormap.from_list("", ["green", "yellow", "orange", "red"], N=1000),
    norm=plt.Normalize(0, 100)
)
ctx.add_basemap(map_sealing, url=ctx.providers.Stamen.TonerLite)
map_sealing.set_axis_off()
plt.savefig(os.path.join(map_pdf, "sealing.pdf"), optimize=True, bbox_inches="tight", pad_inches=0)

# %% [markdown]
# # Fixing Missing Values for Sealing
#
# As described in the documentation of the sealing data set, there are no observations for streets,
# but can be assumed as 100% sealing.
#
# Missing areas are shown as white.
#
# ![Zoomed Sealing Map](../reports//figures/maps/jpg/sealing_zoomed.png)

# %% [markdown]
# `GeoDataFrame`s can do spatial joins. The following keeps the structure of the `df_ground_level`
# and fills missing sealing values with 100%.

# %%
joined = gpd.sjoin(df_ground_level, df_sealing, how="left")
joined["sealing"] = joined["sealing"].fillna(100)
joined.drop(columns=["index_right"], inplace=True)

joined.head()

# %% [markdown]
# Obviously, there are some duplicated rows (See index).
# This happens because it is possible that multiple ground level tiles intersect more than one sealing areas.
#
# To get smoother transitions, average the values for the duplicated tiles (indices) and remove the duplicates.

# %%
duplicates_index = joined[joined.duplicated("geometry", keep=False)].index.unique()

mean_sealing = [joined.loc[index]["sealing"].mean() for index in duplicates_index]
joined.drop_duplicates("geometry", inplace=True)
joined.loc[duplicates_index, "sealing"] = mean_sealing

joined.to_file(os.path.join(data_preprocessed, "joined_ground-level_sealing.geojson"), driver="GeoJSON")
joined.head()

# %% [markdown]
# This is the final data and used in further computations.

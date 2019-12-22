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
from glob import glob

import contextily as ctx
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image

from urban_technologies_berlin.utils import get_tile_square_meter

# %%
data_simulation = os.path.join("../data", "interim", "simulation")

simulation_jpg = os.path.join("../reports/figures/simulation/jpg")
simulation_gif = os.path.join("../reports/figures/simulation/gif")

# %% [markdown]
# Checks for available simulations and parametrize them all.

# %%
simulations = glob(os.path.join(data_simulation, "*"))
simulation_names = [os.path.split(path)[1] for path in simulations]

iterations = len(glob(os.path.join(simulations[0], "*")))

# %%
# first, setup all directories
for directory in [
    simulation_jpg,
    simulation_gif,
    *[os.path.join(simulation_jpg, simulation) for simulation in simulation_names]
]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# %% [markdown]
# ## Visualize the Simulations
#
# Uses the simulated GeoJSON files to visualize the water level.
# So it creates for each iteration one visualization
# and finaly combines them to an animated gif.

# %%
critical_water_level = 30  # in cm

# %%
for simulation in simulation_names:
    for step in range(iterations):

        file_name = f"{simulation}-step-{step}"
        file_path = os.path.join(data_simulation, simulation, file_name + ".geojson")
        data_frame = gpd.read_file(file_path)

        # 100 l water per square meter leads to 10cm of water level
        # -> correspondingly for more square meters
        max_water_level = critical_water_level * 10 * get_tile_square_meter(data_frame)
        min_water_level = 0

        map_water_level = data_frame.to_crs(epsg=3857).plot(
            figsize=(25, 25),
            column="water level",
            alpha=0.5,
            cmap=LinearSegmentedColormap.from_list("", ["green", "yellow", "orange", "red"], N=1000),
            norm=plt.Normalize(min_water_level, max_water_level)
        )

        ctx.add_basemap(map_water_level, url=ctx.providers.Stamen.TonerLite)
        map_water_level.set_axis_off()

        plt.savefig(
            os.path.join(simulation_jpg, simulation, f"{file_name}.jpg"),
            optimize=True,
            bbox_inches="tight",
            pad_inches=0
        )

        # some cleanup to free memory
        plt.close("all")
        del data_frame

    # create the gif file
    image_files = glob(os.path.join(simulation_jpg, simulation, "*.jpg"))
    images = [Image.open(image_file) for image_file in image_files]

    images[0].save(
        os.path.join(simulation_gif, simulation + ".gif"),
        format="GIF",
        append_images=images[1:],
        save_all=True,
        duration=1000,
        loop=0,
        optimize=True
    )

    del images

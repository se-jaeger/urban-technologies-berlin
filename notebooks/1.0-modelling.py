# -*- coding: utf-8 -*-
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

import geopandas as gpd
import numpy as np
from geopandas import GeoDataFrame
from numpy import ndarray

from urban_technologies_berlin.utils import get_tile_size

# %% [markdown]
# ## Algorithm Idea
#
# A very simple algorithm to calculate the water movement is explained in the follwing.
#
# - Loop for $n$ timesteps
#     1. Add rainfall
#     2. Update water level based on water infiltration
#     3. Calculate water movement for each tile independent
#     4. Update water level for each tile
#
# For this some assumptions are necessary.
#
#
# ### Assumptions
#
# - Rainfall is constant in time and geographical dimension
# - Water infiltration based on linear scaling and many simplifications
# - Water movement based on flow formula
#
#
# ## Flow Formula According to Gauckler-Manning-Strickler
# (Source - Wikipedia: https://de.wikipedia.org/wiki/Fließformel#Fließformel_nach_Gauckler-Manning-Strickler)
#
# ${\displaystyle {\begin{aligned}v_{\mathrm {m} }&=k_{\mathrm {st} }\cdot R^{\frac {2}{3}}\cdot
# I^{\frac {1}{2}}\\&=k_{\mathrm {st} }\cdot {\sqrt[{3}]{R^{2}}}\cdot {\sqrt {I}}\end{aligned}}}$
#
#
# - $v_\mathrm m$: "water flow velocity" as $\frac{m}{s}$
# - ${\displaystyle R=\frac{A}{U}}$: "radius" as $m$ -> (corresponds approximately to the water
# depth for very wide, shallow flow cross-sections)
#     - $A$: "flow cross section" as $m^2$
#     - $U$: "wetted perimeter" as $m$
# - $I = \frac{h_f}{L}$: "flow gradient" as $\frac{m}{m}$
#     - $h_f$: "height" as $m$
#     - $L$: "length as $m$
#
#
# | Surface                                   | $k_{st}$ as $\frac{m^{\frac{1}{3}}}{s}$ |
# |-------------------------------------------|---------------------------------------|
# | Smooth concrete                           | 100                                   |
# | Stright watercourse                       | 30 - 40                               |
# | Meandering riverbed with ground vegetation| 20 - 30                               |
# | Torrent with scree                        | 10 - 20                               |
# | Torrent with undergrowth                  | < 10                                  |
#
#
# ## Rainfall Classification
#
# | Rain Classification   | Rainfall in 10 min |
# |-------------|------------------------------|
# | light       | $< 0.5\ mm$ |
# | moderate    | $\ge 0.5\ mm\ \text{&}\ < 1.7\ mm$|
# | strong      | $\ge 1.7\ mm\ \text{&}\ < 8.3\ mm$|
# | very strong | $> 8.3\ mm$|
#
# (Source - Deutscher Wetter Dienst: https://www.dwd.de/DE/service/lexikon/Functions/glossar.html?lv2=101812&lv3=101906

# %% [markdown]
# ## Initialize `data` DataFrame and Convert to Matrix


# %%
def list2matrix(data: ndarray) -> ndarray:
    """
    Converts the ``ndarray`` from list shape (n x columns) into squared matrix shape (sqrt(n) x sqrt(n) x columns).
    """
    if len(data.shape) != 2:
        raise ValueError("Not in 'list' form!")

    tiles_per_direction = int(np.sqrt(data.shape[0]))

    dims = []

    for index in range(data.shape[1]):
        dims.append(data[:, index].reshape((tiles_per_direction, tiles_per_direction)))

    return np.stack(dims, axis=2)


def matrix2list(data: ndarray) -> ndarray:
    """
    Converts the ``ndarray`` from squared matrix shape (sqrt(n) x sqrt(n) x columns) into list shape (n x columns).
    """
    if len(data.shape) != 3:
        raise ValueError("Not in 'matrix' form!")

    dims = []

    for index in range(data.shape[2]):
        dims.append(data[:, :, index].flatten())

    return np.stack(dims, axis=1)


# %%
def init_and_get_list_form(data: GeoDataFrame) -> ndarray:
    """
    Initialize the data ``GeoDataFrame`` with ``water level`` column and convert it into a ``ndarray``.
    """
    data["water level"] = 0
    columns = ["water level", "x gradient", "y gradient", "sealing"]

    return data[columns].values


# %% [markdown]
# ## Water Infiltration
#
# The follwing figure shows some examples for the water infiltration on given constraints.
#
# <img src="../reports/figures/misc/sealing_examples.png" />
#
# **Original:** http://www.stadtentwicklung.berlin.de/umwelt/umweltatlas/e_tab/ta213_03.gif
#
#
# I took the following values as reference points, ignored all other variables, and assumed a linear scale in between.
#
# | Area description | sealing in % | water infiltration in % |
# |------------------|--------------|-------------------------|
# |     Meadows      |     0        |         34              |
# | industrial area  |    96        |          8              |
#
#
# ### Calculations for Water Infiltration
#
# $$infiltration = \frac{\Delta infiltration}{\Delta sealing} + 34 = \frac{-26}{96} sealing + 34$$

# %%
def water_infiltration(data_as_list: ndarray) -> ndarray:
    """
    Calculates and returns the remaining water level after infiltration.
    Based on the above assumptions.
    """
    def get_infiltration(sealing: ndarray) -> ndarray:
        return (-26/96 * sealing + 34) / 100  # because 100% -> needed in [0, 1]

    # 1 - infiltration -> because interested in the remaining water level
    return data_as_list[:, 0] * (1 - get_infiltration(data_as_list[:, 3]))


# %% [markdown]
# ## Calculations for $R$
#
# Approximatly the water depth.
#
# **Properties of Water:**
#
# - $1mm$ precipitation is equal to $1\ \frac{liter}{square\ meter}$ water.
# - $1m^3 = 1000l$
#
# => $height = \frac{1000l}{length * width}$
#
# Because units in `meter` and `liter` are needed:
# $$height = \frac{water\ level}{length * width * 1000} = \frac{water\ level}{tile\ square\ meter * 1000}$$

# %%
def R(water_in_liter: ndarray, tile_square_meter: int) -> ndarray:
    """
    Computes the water depth for ``water_in_liter`` on a tile with ``tile_square_meter``.
    """
    return water_in_liter / (tile_square_meter * 1000)


# %% [markdown]
# ## Calculations for $I$
#
# Gradient of the ground level in `x` and `y` already calculated.

# %% [markdown]
# ## Putting Things Together
#

# %%
def water_flow_velocity(
        data_as_list: ndarray,
        tile_square_meter: int,
        kst: int = 100
) -> float:
    """
    Computes the water flow velocities in ``x`` and ``y`` direction for the given data.

    ``data_as_list`` is list shape.
    """
    water_in_liter = data_as_list[:, 0].reshape((data_as_list.shape[0], 1))
    gradients = data_as_list[:, 1:3]

    gradient_direction = np.sign(gradients)  # to fix issue with negative square roots
    absolute_gradients = np.absolute(gradients)  # use absolute gradients
    result_absolute = kst * np.cbrt(R(water_in_liter, tile_square_meter) ** 2) * np.sqrt(absolute_gradients)

    return gradient_direction * result_absolute  # and restore the actual direction


# %% [markdown]
# ## Calculate Distance for Timestep
#
# To calculate the water level that flows from one tile to another, the flowed distance is needed.

# %%
def water_flow_distance(water_velocities: ndarray, timestep: int = 10) -> ndarray:
    """
    Computes the water flow distance in ``x`` and ``y`` direction.

    ``water_velocities`` is list shape.
    """
    timestep_seconds = timestep * 60

    return water_velocities * timestep_seconds


# %% [markdown]
# ## Calculate the Flow of Water between Tiles
#
# Simplification, only take the flow parallel to the axes into account.

# %%
def water_flow(water_distances: ndarray, tile_size: int) -> ndarray:
    """
    Computes the water flow in ``x`` and ``y`` direction.
    Returns the water flow in percent.

    ``water_distances`` is list shape.
    """
    water_distance_directions = np.sign(water_distances)
    absolute_water_distances = np.absolute(water_distances)

    # used to calculate the percentage water flow
    sum_distances = np.maximum(np.sum(absolute_water_distances, axis=1), tile_size)
    fraction_of_water_flow = absolute_water_distances.T / sum_distances

    return fraction_of_water_flow.T * water_distance_directions


# %% [markdown]
# ## Update the Water Level
#
# The data for `water level`, `water flow x`, and `water flow y` gets concatenated as shown in the following figure.
#
# ![Data Structure](../reports/figures/misc/update_data_structure.pdf)
#
# For a performant calculation of the updated water level,
# the matrix gets shifted in all 4 directions as shown in the following figure.
#
# ![Data Structure](../reports/figures/misc/update_calculation_explanation.pdf)
#
# **Example of the tile with water level `5`:**
#
# To calculate the water that flows into this tile from the right, the `left shifted` matrix is needed. Then:
# 1. If the value for `water flow x` is negative, i.e. flow direction to the left, calculate at the same position:
#     - $water\ level * water\ flow\ x$
#
# Also, calculate for the three other matrices correspondingly.
# For the possibility that not all water moves from one tile to another, calculate the remaining water level.
# -> $input\ water\ level * 1 - (abs(water\ flow\ x) + abs(water\ flow\ y))$
#
# Finally, the new water level of the tile is the sum of the 4 values (from right, left, above, below)
# and the remaining water level.
#
# These calculations are sensible because values for `water flow` are percentage values.
#
# Because numpy arrays are used, the above calculations get applied
# to each and every tile at the same time (in parallel).
#
# **Note:** water at the border can get lost

# %%
def updated_water_level(data_as_matrix: ndarray, water_update_as_matrix: ndarray) -> ndarray:
    """
    Calculates the new water levels. Takes care of the water movement from one to another tile.
    Simplification: Water only flows parallel to the axis.

    ``data_as_matrix`` is matrix shape.
    ``water_update_as_matrix`` is matrix shape.
    """
    if len(data_as_matrix.shape) != 3 or len(water_update_as_matrix.shape) != 3:
        raise ValueError("At least one of the parameters is not in 'matrix' form!")

    # Some index values for convenience
    water_level_index = 0
    water_flow_x_index = 4
    water_flow_y_index = 5

    # combine the input data because it is tile associated
    data = np.concatenate((data_as_matrix, water_update_as_matrix), axis=2)

    # Shift/roll the data matrix in ``x`` and ``y`` dimension in both directions.
    # And supress that the 'overflow' gets reintroduced on the other side of the matrix
    right_shifted = np.roll(data, 1, 1)
    right_shifted[:, 0, :] = 0

    left_shifted = np.roll(data, -1, 1)
    left_shifted[:, -1, :] = 0

    up_shifted = np.roll(data, -1, 0)
    up_shifted[-1, :, :] = 0

    down_shifted = np.roll(data, 1, 0)
    down_shifted[0, :, :] = 0

    # Idea: Calculate each tile of the output separately (vectorized)
    # For the water that flows into the tile from right:
    #       shift left, and if there is water flow to the right calculate the water level
    # For flow to left: shift right, if flow negative (direction is left) claculate water level
    # For y dircetion correspondingly
    water_flow_from_right = np.absolute(
        np.minimum(left_shifted[:, :, water_flow_x_index], 0) * left_shifted[:, :, water_level_index]
    )
    water_flow_from_left = np.absolute(
        np.maximum(right_shifted[:, :, water_flow_x_index], 0) * right_shifted[:, :, water_level_index]
    )
    water_flow_from_above = np.absolute(
        np.minimum(down_shifted[:, :, water_flow_x_index], 0) * down_shifted[:, :, water_level_index]
    )
    water_flow_from_below = np.absolute(
        np.maximum(up_shifted[:, :, water_flow_x_index], 0) * up_shifted[:, :, water_level_index]
    )

    # not necessarily all water leaves the tile
    # Idea: water level old * (100% - (% x-direction - % y-direction))
    # If not 100% of data left the tile, calculate the water level remaining
    x_flow_absolute = np.absolute(data[:, :, water_flow_x_index])
    y_flow_absolute = np.absolute(data[:, :, water_flow_y_index])
    no_water_flow = data[:, :, water_level_index] * (1 - (x_flow_absolute + y_flow_absolute))

    # sum the 5 water movements up -> new updated water levels for each tile
    return water_flow_from_right + water_flow_from_left + water_flow_from_above + water_flow_from_below + no_water_flow


# %% [markdown]
# ## Timestep Based Simulation
#
# Putting all parts together for water movement simulations.

# %%
def simulate(
    data: GeoDataFrame,
    rainfall: int,
    timestep_size: int,
    iterations: int,
    data_path: str = "../data/interim/simulation"
) -> list:
    """
    Runs the actual simulation of the water movement.
    Creates and saves GeoJSON files for each iteration.
    """

    # Some needed values
    tile_size = get_tile_size(data)
    tile_square_meter = tile_size ** 2

    water_levels = []
    data_ndarray = init_and_get_list_form(data_data_frame)

    # create necessary directories
    directory_name = f"tile_size-{tile_size}-rain-{rainfall}"
    directory = os.path.join(data_path, directory_name)

    if not os.path.exists(directory):
        os.makedirs(directory)

    # Run the actual simulation
    for index in range(iterations):

        # add rainfall
        data_ndarray[:, 0] += rainfall * tile_square_meter  # rainfall per square meter

        # infiltration of water
        data_ndarray[:, 0] = water_infiltration(data_ndarray)

        # water movement for each tile
        velocities = water_flow_velocity(data_ndarray, tile_square_meter)
        distances = water_flow_distance(velocities, timestep_size)
        water_update = water_flow(distances, tile_size)

        # update the water levels
        new_water_level = updated_water_level(list2matrix(data_ndarray), list2matrix(water_update)).flatten()
        data_ndarray[:, 0] = new_water_level

        # save the simulation result as data frame
        data["water level"] = new_water_level
        data.to_file(os.path.join(directory, directory_name + f"-step-{index}.geojson"), driver="GeoJSON")
        water_levels.append(new_water_level)


# %%
data_path = os.path.join("../data", "preprocessed", "joined_ground-level_sealing.geojson")
data_data_frame = gpd.read_file(data_path)

rainfall = 1
time_step_size = 1
iterations = 30

# %%
simulate(data_data_frame, rainfall, time_step_size, iterations)

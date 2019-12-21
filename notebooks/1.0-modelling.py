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

from urban_technologies_berlin.utils import get_tile_size, get_tile_square_meter

# %%
data_path = os.path.join("../data", "preprocessed", "joined_ground-level_sealing.geojson")
data = gpd.read_file(data_path)


# %% [markdown]
# ## Assumptions
#
# - Rainfall is constant in time and geographical dimension
# - Water infiltration: $100\% - sealing$ of water level each step
# - Water movement based on following formula
#
# ## Flow Formula according to Gauckler-Manning-Strickler
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
# | ligth       | $< 0.5\ mm$ |
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
    columns = ["water level", "x gradient", "y gradient", "sealing"]
    tiles_per_direction = int(np.sqrt(data.shape[0]))
    
    data["water level"] = 0

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
#
#
# ## TODO - Algorithm Idea
#
# 1. Init with rain on each tile
# 2. Loop for $n$ timesteps
#     1. Update water level based on water infiltration
#     2. Calculate water movement for each tile independent
#     3. Update water level for each tile
#     4. Add new rainfall

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
# $$height = \frac{water\ amount}{length * width * 1000} = \frac{water\ amount}{tile\ square\ meter * 1000}$$

# %%
def R(water_in_liter: ndarray, tile_square_meter: int) -> ndarray:
    """
    Computes the water depth for ``water_in_liter`` on a tile with ``tile_square_meter``.

    Args:
        water_in_liter (ndarray): Vector of shape ``n x 1`` of water measurements.
        tile_square_meter (int): Square meters of one tile.

    Returns:
        ndarray: Vector of shape ``n x 1``, water depth for each of the n tiles.
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
        water_in_liter: ndarray,
        gradients: ndarray,
        tile_square_meter: int,
        kst: int = 100
    ) -> float:
    """
    Computes the water flow velocities in ``x`` and ``y`` direction for given water levels and gradients of a tile.

    Args:
        water_in_liter (ndarray): Vector of shape ``n x 1`` of water measurements.
        gradients (ndarray): Matrix of shape ``n x 2`` of gradients in ``x`` and ``y`` direction.
        tile_square_meter (int): Square meters of one tile.
        kst (int, optional): Constant value for specific surface. Defaults to 100.

    Returns:
        ndarray: Matrix of the water flow velocities of shape ``n x 2`` in ``x`` and ``y`` direction.
    """
    gradient_direction = np.sign(gradients)
    result_absolute = kst * np.cbrt(R(water_in_liter, tile_square_meter) ** 2) * np.sqrt(np.absolute(gradients))

    return gradient_direction * result_absolute


# %% [markdown]
# ## Initialize `data` DataFrame and Convert to Matrix

# %%
def init_and_get_matrix(data: GeoDataFrame) -> ndarray:
    """
    Initialize the data ``GeoDataFrame`` with ``water level`` column and convert int into a ``ndarray``.
    
    Args:
        data (``GeoDataFrame``): The data.
    
    Returns:
        ``ndarray``: The data as ``ndarray`` matrix.
    """
    data["water level"] = 0
    columns = ["height", "y gradient", "x gradient", "sealing", "water level"]
    tiles_per_direction = int(np.sqrt(data.shape[0]))
    
    return np.array(data[columns]).reshape((tiles_per_direction, tiles_per_direction, len(columns)))


# %% [markdown]
# ## Calculate Distance for Timestep
#
# To calculate the amount of water that flows from one tile to another, the flowed distance is needed.

# %%
def water_flow_distance(water_velocities: ndarray, timestep: int = 10) -> ndarray:
    """
    Computes the water flow distance in ``x`` and ``y`` direction.

    Args:
        water_velocities (ndarray): Matrix of the water flow velocities of shape ``n x 2`` in ``x`` and ``y`` direction.
        timestep (int, optional): Minutes for one timestep. Defaults to 10.

    Returns:
        flondarrayat: Matrix of the water flow distances of shape ``n x 2`` in ``x`` and ``y`` direction.
    """
    timestep_seconds = timestep * 60

    return water_velocities * timestep_seconds


# %% [markdown]
# ## Simulate the Flow of Water between Tiles
#
# Simplification, only take the flow parallel to the axes into account.

# %%
def water_flow(water_distances: ndarray, tile_size: int) -> ndarray:
    """
    Computes the water flow in ``x`` and ``y`` direction.

    Args:
        water_distances (ndarray): Matrix of the water flow distances of shape ``n x 2`` in ``x`` and ``y`` direction.
        tile_size (int): Square meter for one tile.

    Returns:
        ndarray: Matrix of water flow in percentages of shape ``n x 2`` in ``x`` and ``y`` direction.
    """
    water_distance_directions = np.sign(water_distances)
    absolute_water_distances = np.absolute(water_distances)

    # used to calculate the percentage water flow
    sum_distances = np.maximum(np.sum(absolute_water_distances, axis=1), tile_size)
    fraction_of_water_flow = absolute_water_distances.T / sum_distances

    return fraction_of_water_flow.T * water_distance_directions


# %% [markdown]
# ## Update the Water Level

# %%

# %%

# %%

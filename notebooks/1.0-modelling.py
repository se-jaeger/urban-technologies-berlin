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
def R(water_in_liter: int, tile_square_meter: int) -> float:
    """
    Computes the water depth for ``water_in_liter`` on a tile with ``tile_square_meter``.

    Args:
        water_in_liter (int): Vector of shape ``n x 1`` of water measurements.
        tile_square_meter (int): Square meters of one tile.

    Returns:
        float: Vector of shape ``n x 1``, water depth for each of the n tiles.
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
        water_in_liter: int,
        gradients: (float, float),
        tile_square_meter: int,
        kst: int = 100
    ) -> (float, float):
    """
    Computes the water flow velocities in ``x`` and ``y`` direction for given water levels and gradients of a tile.

    Args:
        water_in_liter (int): Vector of shape ``n x 1`` of water measurements.
        gradients ([type]): Matrix of shape ``n x 2`` of gradients in ``x`` and ``y`` direction.
        tile_square_meter (int): Square meters of one tile.
        kst (int, optional): Constant value for specific surface. Defaults to 100.

    Returns:
        float: Matrix of the water flow velocities of shape ``n x 2`` in ``x`` and ``y`` direction.
    """
    gradient_direction = np.sign(gradients)
    result_absolute = kst * np.cbrt(R(water_in_liter, tile_square_meter) ** 2) * np.sqrt(np.absolute(gradients))

    return gradient_direction * result_absolute


# %% [markdown]
# ## Calculate Distance for Timestep
#
# To calculate the amount of water that flows from one tile to another, the flowed distance is needed.

# %%
def water_flow_distance(water_velocities: float, timestep: int = 10) -> float:
    """
    [summary]

    Args:
        water_velocities (float): Matrix of the water flow velocities of shape ``n x 2`` in ``x`` and ``y`` direction.
        timestep (int, optional): Minutes for one timestep. Defaults to 10.

    Returns:
        float:: [description]
    """
    timestep_seconds = timestep * 60

    return water_velocities * timestep_seconds


# %%

# %%

# %%

# %%
geometry_coordinates = data[:1]["geometry"].values[0].exterior.xy[0]

tile_size = int(geometry_coordinates[1] - geometry_coordinates[0])
tile_square_meter = tile_size ** 2  # this is okey because they are always squares

# %%

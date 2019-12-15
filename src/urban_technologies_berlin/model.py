import numpy as np
from geopandas import GeoDataFrame
from numpy import ndarray


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


def water_flow_velocity(
        water_in_liter: ndarray,
        gradients: ndarray,
        tile_square_meter: int,
        kst: int = 100
    ) -> ndarray:
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


def water_flow_distance(water_velocities: ndarray, timestep: int = 10) -> ndarray:
    """
    Computes the water flow distance in ``x`` and ``y`` direction.

    Args:
        water_velocities (ndarray): Matrix of the water flow velocities of shape ``n x 2`` in ``x`` and ``y`` direction.
        timestep (int, optional): Minutes for one timestep. Defaults to 10.

    Returns:
        ndarray: Matrix of the water flow distances of shape ``n x 2`` in ``x`` and ``y`` direction.
    """
    timestep_seconds = timestep * 60

    return water_velocities * timestep_seconds


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

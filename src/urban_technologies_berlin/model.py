import numpy as np


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
    return kst * np.cbrt(R(water_in_liter, tile_square_meter) ** 2) * np.sqrt(gradients)

from geopandas import GeoDataFrame


def get_tile_size(data: GeoDataFrame) -> int:
    """
    Helper function that returns the size of a tile.

    Args:
        data (GeoDataFrame): Data that has the form of ground level information.

    Returns:
        int: Tile size in meter. Tiles are always squares.
    """
    geometry_coordinates = data[:1]["geometry"].values[0].exterior.xy[0]

    return int(geometry_coordinates[1] - geometry_coordinates[0])


def get_tile_square_meter(data: GeoDataFrame) -> int:
    """
    Helper funciton that computes the square meter of the given ``data``.

    Args:
        data (GeoDataFrame): Data that has the form of ground level information.

    Returns:
        int: Square meter for one tile.
    """
    return get_tile_size(data) ** 2  # this is okey because they are always squares

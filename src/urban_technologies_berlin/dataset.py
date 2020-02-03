import os
from functools import reduce
from glob import glob

import click
import geopandas as gpd
from berlin_gelaendemodelle_downloader.download import download_data

from .constant import COMPRESS_HELP
from .utils import get_tile_size


@click.group()
def entrypoint():
    """
    Gives functionality to create the combined dataset: Sealing and Ground Level of Berlin
    This CLI assumes and only works with the project structure given by:
        https://github.com/se-jaeger/urban-technologies-berlin
    """


@entrypoint.command()
@click.option("--download", is_flag=True, type=bool, help="flag to download ground level data first")
@click.option("--compress", type=int, default=5, help=COMPRESS_HELP)
def create_dataset(download: bool, compress: int):
    """
    Create the combined dataset: Sealing and Ground Level of Berlin
    Assumes and only works with the project structure given by:
        https://github.com/se-jaeger/urban-technologies-berlin
    """

    # some necessary values
    path = "data/preprocessed"
    file_name = "ground-level_sealing.geojson"
    subset_path = "data/raw/ground_level"
    sealing = "data/interim/sealing/sealing.geojson"

    # download the data
    if download:
        click.echo(f"Download data and compress to {compress}x{compress}m pixel")

        if not os.path.exists(subset_path):
            os.mkdir(subset_path)

        download_data(
            download_path="data/raw/ground_level",
            keep_original=False,
            compress=compress,
            file_format=("geojson",)
        )

    # read all ground level subsets and combine to one
    file_paths = glob(os.path.join(subset_path, "*.geojson"))
    click.echo(f"Found {len(file_paths)} files in: {subset_path}")
    geojson_files = [gpd.read_file(file) for file in file_paths]

    combined = reduce(lambda a, b: a.append(b), geojson_files)
    combined.reset_index(drop=True, inplace=True)

    pixel_size = get_tile_size(combined)
    click.echo(f"All files read, pixel size is {pixel_size}x{pixel_size}m")

    # read sealing data and join both data sets
    df_sealing = gpd.read_file(sealing)
    joined = gpd.sjoin(combined, df_sealing, how="left")

    click.echo("Sealing and Ground Level joined")

    # fix missing values (streets) and duplicats
    joined["sealing"] = joined["sealing"].fillna(100)
    joined.drop(columns=["index_right"], inplace=True)
    duplicates_index = joined[joined.duplicated("geometry", keep=False)].index.unique()

    mean_sealing = [joined.loc[index]["sealing"].mean() for index in duplicates_index]
    joined.drop_duplicates("geometry", inplace=True)
    joined.loc[duplicates_index, "sealing"] = mean_sealing

    click.echo("Fixed duplicated pixels.")

    if not file_name.endswith(".geojson"):
        click.secho("file-name need to end with '.geojson' -> added it for you", fg="red")
        file_name += ".geojson"

    click.echo("Saving file ...")
    joined.to_file(os.path.join(path, file_name), driver="GeoJSON")
    click.secho("Done!", fg="green")

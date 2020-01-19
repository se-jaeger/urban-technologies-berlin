import click


@click.group()
def entrypoint():
    """
    Entrypoint to create the whole dataset.
    """


@entrypoint.command()
def create_dataset():
    """
    Subcommand to create the whole dataset.
    """

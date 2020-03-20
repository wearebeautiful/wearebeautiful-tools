import sys
import os
import click

from wearebeautiful.database import create_database
import config

MODEL_DIR = "/archive/model-archive"
MODEL_GIT_DIR = "/archive/git-model-repo"

@click.command()
def create():
    create_database(os.path.join(config.MODEL_GIT_DIR, "wab-models.db"), config.MODEL_DIR)


def usage(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


if __name__ == "__main__":
    print("create_db.py running, made with sleepiness and love in the maker cave <3\n")
    create()
    sys.exit(0)

import sys
import os
import click

from wearebeautiful.database import create_database

@click.command()
@click.argument("db_file", nargs=1)
@click.argument("model_dir", nargs=1)
def create(db_file, model_dir):
    create_database(db_file, model_dir)


def usage(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


if __name__ == "__main__":
    print("create_db.py running, made with sleepiness and love in the maker cave <3\n")
    create()
    sys.exit(0)

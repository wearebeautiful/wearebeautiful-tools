import sys
import os
import click

from wearebeautiful.database import create_database
import config


@click.command()
def create():
    create_database()


def usage(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


if __name__ == "__main__":
    print("create_db.py running, made with sleepiness and love in the maker cave <3\n")
    create()
    sys.exit(0)

import os
import sys
import json
import shutil
import click
from wearebeautiful.process import process_surface

@click.command()
@click.argument("id", nargs=1)
@click.argument("code", nargs=1)
def process(id, code):
    process_surface(id, code)


def usage(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


if __name__ == "__main__":
    print("process_surface.py running, made with high quality love in Barcelona. <3\n")
    process()
    sys.exit(0)

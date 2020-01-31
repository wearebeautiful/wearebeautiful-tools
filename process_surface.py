import os
import sys
import json
import shutil
import click
from wearebeautiful.process import process_surface

@click.command()
@click.argument("manifest", nargs=1)
@click.argument("surface", nargs=1)
@click.argument("dest_dir", nargs=1)
def process(manifest, surface, dest_dir):
    process_surface(manifest, surface, dest_dir)


def usage(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


if __name__ == "__main__":
    print("process_surface.py running, made with high quality love in Barcelona. <3\n")
    process()
    sys.exit(0)

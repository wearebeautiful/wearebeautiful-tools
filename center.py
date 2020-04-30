import os
import sys
import json
import shutil
import click
from wearebeautiful.process import center_mesh

@click.command()
@click.argument("filename", nargs=1)
def center(filename):
    center_mesh(filename)


def usage(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


if __name__ == "__main__":
    print("center.py running, made with high quality, but illegal lockdown love in Barcelona. <3\n")
    center()
    sys.exit(0)

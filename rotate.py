import os
import sys
import json
import shutil
import click
from wearebeautiful.process import rotate_mesh

@click.command()
@click.argument("filename", nargs=1)
@click.argument("rot_x", nargs=1, type=float)
@click.argument("rot_y", nargs=1, type=float)
@click.argument("rot_z", nargs=1, type=float)
def rotate(filename, rot_x, rot_y, rot_z):
    rotate_mesh(filename, rot_x, rot_y, rot_z)


def usage(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


if __name__ == "__main__":
    print("rotate mesh.py running, made with high quality love in Barcelona. <3\n")
    rotate()
    sys.exit(0)

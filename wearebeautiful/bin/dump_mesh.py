#!/usr/bin/env python

import sys
import os
from time import time
import numpy as np

import pymesh
import click

@click.command()
@click.argument("src_file", nargs=1)
def invert(src_file):

    src_file = os.path.join("/src", src_file)
    mesh = pymesh.meshio.load_mesh(src_file);

#    print("vertices")
#    for vertex in mesh.vertices:
#        print(vertex)

    print("faces")
    for face in mesh.faces:
        print(face)


def usage(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


if __name__ == "__main__":
    print("dump_mesh.py running, made with love and netherlands's finest in Delft. <3\n")
    invert()
    sys.exit(0)

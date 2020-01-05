#!/usr/bin/env python

"""
Flip the normals on the mesh to turn it inside out
"""
import sys
import os
from time import time
import numpy as np

import pymesh
import click

from wearebeautiful.scale_mesh import flip_mesh


@click.command()
@click.argument("src_file", nargs=1)
@click.argument("dest_file", nargs=1)
def invert(src_file, dest_file):

    src_file = os.path.join("/src", src_file)
    dest_file = os.path.join("/dest", dest_file)

    mesh = pymesh.meshio.load_mesh(src_file);

    print("start: %d vertexes, %d faces." % (mesh.num_vertices, mesh.num_faces))
    mesh = flip_mesh(mesh)
    print(" flip: %d vertexes, %d faces." % (mesh.num_vertices, mesh.num_faces))

    pymesh.meshio.save_mesh(dest_file, mesh);


def usage(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


if __name__ == "__main__":
    print("invert_mesh.py running, made with love and cooties in Delft. <3\n")
    invert()
    sys.exit(0)

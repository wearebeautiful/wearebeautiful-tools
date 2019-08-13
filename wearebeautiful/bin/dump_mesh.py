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

    src_path = os.path.join("/src", src_file)
    mesh = pymesh.meshio.load_mesh(src_path);
    mesh = pymesh.compute_outer_hull(mesh);

    print("model %s" % src_file)
    print(" vertices: %6d" % mesh.num_vertices)
    print("    faces: %3d" % mesh.num_faces)
    print("dimension: (%-.5f %-.5f %-.5f)" % (mesh.bbox[1][0] - mesh.bbox[0][0],
                                  mesh.bbox[1][1] - mesh.bbox[0][1], 
                                  mesh.bbox[1][2] - mesh.bbox[0][2]))


def usage(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


if __name__ == "__main__":
    print("dump_mesh.py running, made with love and netherlands's finest in Delft. <3\n")
    invert()
    sys.exit(0)

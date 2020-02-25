#!/usr/bin/env python3

import sys
import os
from time import time
import numpy as np
from wearebeautiful.utils import get_fast_bbox

import pymesh
import click

@click.command()
@click.argument("src_file", nargs=1)
def invert(src_file):

    mesh = pymesh.meshio.load_mesh(src_file);
    bbox = get_fast_bbox(mesh)

    print("model %s" % src_file)
    print(" vertices: %8s" % ("{:,}".format(mesh.num_vertices)))
    print("    faces: %8s" % ("{:,}".format(mesh.num_faces)))
    print("dimension: (%-.5f %-.5f %-.5f)" % (bbox[1][0] - bbox[0][0],
                                  bbox[1][1] - bbox[0][1], 
                                  bbox[1][2] - bbox[0][2]))
    print("is manifold: ", mesh.is_manifold())
    print("is edge manifold: ", mesh.is_edge_manifold())
    print("is vertex manifold: ", mesh.is_vertex_manifold())
    print("is closed: ", mesh.is_closed())
    print("is oriented: ", mesh.is_oriented())
    print("attribute names: ", mesh.attribute_names)


def usage(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


if __name__ == "__main__":
    print("dump_mesh.py running, made with love and netherlands's finest in Delft. <3\n")
    invert()
    sys.exit(0)

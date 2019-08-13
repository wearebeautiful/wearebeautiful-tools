#!/usr/bin/env python

"""
Dumbass mesh scale function
"""
import sys
import os
from time import time
import numpy as np

import pymesh
import click

def asplode_mesh(mesh, scale):
    new_faces = []
    for face in mesh.faces:
        new_face = []
        for f in list(face):
            new_face.append(f * scale)

        new_faces.append(new_face)

    return pymesh.form_mesh(mesh.vertices, np.array(new_faces))


@click.command()
@click.argument("scale", nargs=1, type=float)
@click.argument("src_file", nargs=1)
def asplode(scale, src_file):

    stl_file = os.path.join("/src", src_file)
    mesh = pymesh.meshio.load_mesh(stl_file);
    pymesh.meshio.save_mesh(stl_file, asplode_mesh(mesh, scale));


def usage(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


if __name__ == "__main__":
    print("asplode_mesh.py running, silliness im dorf. <3\n")
    asplode()
    sys.exit(0)

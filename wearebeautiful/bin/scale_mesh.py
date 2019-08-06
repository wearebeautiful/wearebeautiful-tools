#!/usr/bin/env python

"""
Remesh the input mesh to remove degeneracies and improve triangle quality.
"""
import sys
import os
from time import time
import numpy as np

import pymesh
import click

def fix_mesh(mesh, target_len):
    bbox_min, bbox_max = mesh.bbox;
    diag_len = np.linalg.norm(bbox_max - bbox_min);

    count = 0;
    print("  remove degenerated triangles")
    mesh, __ = pymesh.remove_degenerated_triangles(mesh, 100);
    print("  split long edges")
    mesh, __ = pymesh.split_long_edges(mesh, target_len);
    num_vertices = mesh.num_vertices;
    while True:
        print("  pass %d" % count)
        print("    collapse short edges #1")
        mesh, __ = pymesh.collapse_short_edges(mesh, 1e-6);
        print("    collapse short edges #2")
        mesh, __ = pymesh.collapse_short_edges(mesh, target_len,
                preserve_feature=True);
        print("    remove obtuse triangles")
        mesh, __ = pymesh.remove_obtuse_triangles(mesh, 150.0, 100);
        print("    %d of %s vertices." % (num_vertices, mesh.num_vertices))

        if mesh.num_vertices == num_vertices:
            break;

        num_vertices = mesh.num_vertices;
        count += 1;
        if count > 10: break;

    print("  resolve self intersection")
    mesh = pymesh.resolve_self_intersection(mesh);
    print("  remove duplicated faces")
    mesh, __ = pymesh.remove_duplicated_faces(mesh);
    print("  computer outer hull")
    mesh = pymesh.compute_outer_hull(mesh);
    print("  remove duplicated faces")
    mesh, __ = pymesh.remove_duplicated_faces(mesh);
    print("  remove obtuse triangles")
    mesh, __ = pymesh.remove_obtuse_triangles(mesh, 179.0, 5);
    print("  remove isolated vertices")
    mesh, __ = pymesh.remove_isolated_vertices(mesh);

    return mesh;


def flip_mesh(mesh):
    new_faces = []
    for face in mesh.faces:
        new_face = list(face)
        new_face.reverse()
        new_faces.append(new_face)

    return pymesh.form_mesh(mesh.vertices, np.array(new_faces))


def scale_mesh(invert, target_len, in_file, out_file):

    mesh = pymesh.meshio.load_mesh(in_file);

    print("start: %d vertexes, %d faces." % (mesh.num_vertices, mesh.num_faces))
    mesh = fix_mesh(mesh, target_len);
    print("  fix: %d vertexes, %d faces." % (mesh.num_vertices, mesh.num_faces))

    if invert:
        mesh = flip_mesh(mesh)
        print(" flip: %d vertexes, %d faces." % (mesh.num_vertices, mesh.num_faces))

    pymesh.meshio.save_mesh(out_file, mesh);


@click.command()
@click.option('--invert/--no-invert', default=False, help='Flip the normals on the STL file')
@click.argument("len", nargs=1, type=float)
@click.argument("src_dir", nargs=1)
@click.argument("dest_dir", nargs=1)
def scale(invert, len, src_dir, dest_dir):

    filenames = os.listdir(src_dir)
    if not filenames:
        print("The src directory is empty, numbnutz.")
        sys.exit(-1)

    for filename in filenames:
        if filename.lower().endswith(".stl") or filename.lower().endswith(".obj"):
            if filename.lower().endswith(".obj"):
                dest_filename = os.path.splitext(filename)[0] + ".stl"
            else:
                dest_filename = filename

            print("%s -> %.2f" % (dest_filename, len))
            t0 = time()
            scale_mesh(invert, len, os.path.join(src_dir, filename), os.path.join(dest_dir, dest_filename))
            print("  done with file. %d seconds elapsed.\n" % (time() - t0))
        else:
            print("Igorning file '%s', is not STL nor OBJ." % filename)

    print("\ndone with all files.")


def usage(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


if __name__ == "__main__":
    print("scale_mesh.py running, making STL files. <3\n")
    scale()
    sys.exit(0)

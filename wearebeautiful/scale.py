import sys
import os
import math
import tempfile
from time import time
import numpy as np
from wearebeautiful.utils import flip_mesh, center_around_origin

import pymesh

def fix_mesh(mesh, target_len):
    bbox_min, bbox_max = mesh.bbox;
    diag_len = np.linalg.norm(bbox_max - bbox_min);

    print("running downsample mesh to len %.3f" % target_len)
    count = 0;
    mesh, __ = pymesh.split_long_edges(mesh, target_len);
    num_vertices = mesh.num_vertices;
    while True:
        mesh, __ = pymesh.collapse_short_edges(mesh, 1e-6);
        mesh, __ = pymesh.collapse_short_edges(mesh, target_len,
                preserve_feature=True);

        if mesh.num_vertices == num_vertices:
            break;

        num_vertices = mesh.num_vertices;
        count += 1;
        if count > 10: break;

    return mesh;


def downsample_mesh(invert, target_size, in_file, out_file):

    min_file_size = target_size * .9
    max_file_size = target_size * 1.1

    file_size = os.path.getsize(in_file)
    mesh = pymesh.meshio.load_mesh(in_file);

    temp_file = "/tmp/temp.stl"
    segment_len = .40
    last_size = None
    increment = .1
    if file_size > max_file_size:
        print("initial size: %sKb, target size: %sKb" % (f'{file_size // 1024:,}', f'{target_size // 1024:,}'))
        while True:
            mesh = fix_mesh(mesh, segment_len)
            pymesh.meshio.save_mesh(temp_file, mesh);
            new_size = os.path.getsize(temp_file)
            print("size: %sKb" % (f'{new_size // 1024:,}'))

            if new_size <= max_file_size and new_size >= min_file_size:
                break

            done = False
            if last_size:
                if new_size > max_file_size and last_size < min_file_size:
                    increment /= 2.0
                    segment_len += increment
                    done = True
                elif new_size < min_file_size and last_size > max_file_size:
                    increment /= 2.0
                    segment_len -= increment
                    done = True

            if not done: 
                diff = abs(target_size - new_size)
                if diff > (target_size * 3):
                    adjust = 3
                elif diff > (target_size * 2):
                    adjust = 2
                else:
                    adjust = 1
                if new_size > target_size:
                    segment_len += (adjust * increment)
                else:
                    segment_len -= (adjust * increment)

            mesh = pymesh.meshio.load_mesh(in_file);
            last_size = new_size

    try:
        os.unlink(temp_file)
    except IOError:
        pass

    mesh, __ = pymesh.remove_degenerated_triangles(mesh, 100);
    mesh = center_around_origin(mesh)
    pymesh.meshio.save_mesh(out_file, mesh);


def scale_mesh(invert, len, in_file, out_file):

    mesh = pymesh.meshio.load_mesh(in_file);

    mesh = fix_mesh(mesh, len);
    mesh, __ = pymesh.remove_degenerated_triangles(mesh, 100);
    mesh = center_around_origin(mesh)

    if mesh.num_vertices == 0 or mesh.num_faces == 0:
        printf("ERROR: segment len is too small, no vertices/faces are left.")
        return

    if invert:
        mesh = flip_mesh(mesh)
        print(" flip: %d vertexes, %d faces." % (mesh.num_vertices, mesh.num_faces))

    pymesh.meshio.save_mesh(out_file, mesh);

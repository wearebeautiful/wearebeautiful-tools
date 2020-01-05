import sys
import os
from time import time
import numpy as np
from wearebeautiful.utils import flip_mesh, center_around_origin

import pymesh

def fix_mesh(mesh, target_len, opts):
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

        if opts['cleanup']:
            print("    remove obtuse triangles")
            mesh, __ = pymesh.remove_obtuse_triangles(mesh, 150.0, 100);
            print("    %d of %s vertices." % (num_vertices, mesh.num_vertices))

        if mesh.num_vertices == num_vertices:
            break;

        num_vertices = mesh.num_vertices;
        count += 1;
        if count > 10: break;

    if opts['cleanup']:
        print("  resolve self intersection")
        mesh = pymesh.resolve_self_intersection(mesh);
        print("  remove duplicated faces")
        mesh, __ = pymesh.remove_duplicated_faces(mesh);
#        print("  computer outer hull")
#        mesh = pymesh.compute_outer_hull(mesh);
        print("  remove duplicated faces")
        mesh, __ = pymesh.remove_duplicated_faces(mesh);
        print("  remove obtuse triangles")
        mesh, __ = pymesh.remove_obtuse_triangles(mesh, 179.0, 5);
        print("  remove isolated vertices")
        mesh, __ = pymesh.remove_isolated_vertices(mesh);

    return mesh;


def scale_mesh(invert, len, in_file, out_file, opts):

    mesh = pymesh.meshio.load_mesh(in_file);

    print("start: %d vertexes, %d faces." % (mesh.num_vertices, mesh.num_faces))
    mesh = fix_mesh(mesh, len, opts);
    mesh = center_around_origin(mesh)
    print("  fix: %d vertexes, %d faces." % (mesh.num_vertices, mesh.num_faces))

    if mesh.num_vertices == 0 or mesh.num_faces == 0:
        printf("ERROR: segment len is too small, no vertices/faces are left.")
        return

    if invert:
        mesh = flip_mesh(mesh)
        print(" flip: %d vertexes, %d faces." % (mesh.num_vertices, mesh.num_faces))

    pymesh.meshio.save_mesh(out_file, mesh);

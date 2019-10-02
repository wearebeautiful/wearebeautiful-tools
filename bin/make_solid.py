#!/usr/bin/env python

import sys
import os
import copy
from time import time
import numpy as np
from math import fabs, pow, sqrt
from transform import rotate, scale, translate, get_fast_bbox, invert

import pymesh
import click


BBOX_SHRINK_MM = 1
OUTER_BOX_MM = 15
MAGNET_RADIUS = 30 / 2.0
MAGNET_DEPTH = 3.5
HOOK_BOX_HEIGHT = 10
HOOK_BOX_WIDTH = 5
HOOK_BOX_DEPTH = 10 

def apply_id(mesh):

    bbox = get_fast_bbox(mesh)
    print(bbox)

    bbox[0][0] += BBOX_SHRINK_MM
    bbox[0][1] += BBOX_SHRINK_MM

    bbox[1][0] -= BBOX_SHRINK_MM
    bbox[1][1] -= BBOX_SHRINK_MM

    inner_box_dims = copy.deepcopy(bbox)

    inner_box = pymesh.generate_box_mesh(bbox[0], bbox[1])

    bbox[0][0] -= OUTER_BOX_MM
    bbox[0][1] -= OUTER_BOX_MM
    bbox[0][2] -= OUTER_BOX_MM

    bbox[1][0] += OUTER_BOX_MM
    bbox[1][1] += OUTER_BOX_MM

    print("make box")
    outer_box = pymesh.generate_box_mesh(bbox[0], bbox[1])
    outer_box = pymesh.boolean(outer_box, inner_box, operation="difference", engine="igl")

    magnet_center = (inner_box_dims[0][0] + (inner_box_dims[1][0] - inner_box_dims[0][0]) / 2.0, 
                     inner_box_dims[0][1] + (inner_box_dims[1][1] - inner_box_dims[0][1]) / 2.0,
                     inner_box_dims[0][2])
    magnet_center_top = (inner_box_dims[0][0] + (inner_box_dims[1][0] - inner_box_dims[0][0]) / 2.0, 
                         inner_box_dims[0][1] + (inner_box_dims[1][1] - inner_box_dims[0][1]) / 2.0,
                         inner_box_dims[0][2] + MAGNET_DEPTH)
    magnet_cup = pymesh.generate_cylinder(magnet_center, magnet_center_top, MAGNET_RADIUS, MAGNET_RADIUS - .5, num_segments=64)
    outer_box = pymesh.boolean(outer_box, magnet_cup, operation="union", engine="igl")

    hook_center = (inner_box_dims[1][0] - (inner_box_dims[1][0] - inner_box_dims[0][0]) / 8.0, 
                   inner_box_dims[0][1] + (inner_box_dims[1][1] - inner_box_dims[0][1]) / 2.0,
                   inner_box_dims[0][2])

    hook_box = pymesh.generate_box_mesh((hook_center[0] - (HOOK_BOX_WIDTH / 2),
                                         hook_center[1] - (HOOK_BOX_HEIGHT / 2),
                                         hook_center[2] - (HOOK_BOX_DEPTH / 2)),
                                        (hook_center[0] + (HOOK_BOX_WIDTH / 2),
                                         hook_center[1] + (HOOK_BOX_HEIGHT / 2),
                                         hook_center[2] + (HOOK_BOX_DEPTH / 2)))
    outer_box = pymesh.boolean(outer_box, hook_box, operation="union", engine="igl")

    if 1:
        print("make code")
        code = pymesh.meshio.load_mesh("input/883440VSNN.stl")

        print("rotate")
        code = rotate(code, (0,0,0), (1, 0, 0), 90)
        code = rotate(code, (0,0,0), (0, 0, 1), 180)

        print("scale")
        cbox = get_fast_bbox(code)
        code_w = cbox[1][0] - cbox[0][0]
        box_w = inner_box_dims[1][0] - inner_box_dims[0][0]
        print("box w", box_w)
        print("code w", code_w)
        scale_x = (box_w * .7)  / code_w
        print("scale ", scale_x)
        code = scale(code, scale_x)

        print("translate")
        cbox = get_fast_bbox(code)
        code_w = cbox[1][0] - cbox[0][0]
        trans_x = (code_w / 2.0) + ((box_w - code_w) / 2.0)
        trans_z = (cbox[1][2] - cbox[0][2]) * .15
        code = translate(code, (trans_x,0,-trans_z))

        print("glue")
        outer_box = pymesh.boolean(outer_box, code, operation="union", engine="igl")


    print("make url")
    url = pymesh.meshio.load_mesh("input/wearebeautiful.info.stl")

    print("rotate")
    url = rotate(url, (0,0,0), (1, 0, 0), 90)
#    url = rotate(url, (0,0,0), (0, 0, 1), 180)

    print("scale")
    ubox = get_fast_bbox(url)
    url_w = ubox[1][0] - ubox[0][0]
    box_w = inner_box_dims[1][0] - inner_box_dims[0][0]
    print("box w", box_w)
    print("url w", url_w)
    scale_x = (box_w * .7)  / url_w
    print("scale ", scale_x)
    url = scale(url, scale_x)

    print("translate")
    ubox = get_fast_bbox(url)
    url_w = ubox[1][0] - ubox[0][0]
    trans_x = (url_w / 2.0) + ((box_w - url_w) / 2.0)
    trans_y = inner_box_dims[0][1]
    trans_z = (ubox[1][2] - ubox[0][2]) * .20
    url = translate(url, (trans_x,trans_y,-trans_z))

    print("glue")
    outer_box = pymesh.boolean(outer_box, url, operation="union", engine="igl")
#    return outer_box

    print("final subtract")
    return pymesh.boolean(mesh, outer_box, operation="difference", engine="igl")


def show_bounding_box(mesh): 

    bbox = get_fast_bbox(mesh)

    new_z = bbox[0][2] + 10
    print("bbox: ", bbox)
    print("new z: %.f" % new_z)

    bb_point_mesh_0 = pymesh.generate_icosphere(5.0, (bbox[0][0], bbox[0][1], bbox[0][2])) 
    bb_point_mesh_1 = pymesh.generate_icosphere(5.0, (bbox[1][0], bbox[0][1], bbox[0][2])) 
    bb_point_mesh_2 = pymesh.generate_icosphere(5.0, (bbox[0][0], bbox[1][1], bbox[0][2])) 
    bb_point_mesh_3 = pymesh.generate_icosphere(5.0, (bbox[1][0], bbox[1][1], bbox[0][2])) 
    bb_point_mesh_4 = pymesh.generate_icosphere(5.0, (bbox[0][0], bbox[0][1], bbox[1][2])) 
    bb_point_mesh_5 = pymesh.generate_icosphere(5.0, (bbox[1][0], bbox[0][1], bbox[1][2])) 
    bb_point_mesh_6 = pymesh.generate_icosphere(5.0, (bbox[0][0], bbox[1][1], bbox[1][2])) 
    bb_point_mesh_7 = pymesh.generate_icosphere(5.0, (bbox[1][0], bbox[1][1], bbox[1][2])) 

    print("union 0")
    new = pymesh.boolean(bb_point_mesh_0, bb_point_mesh_1, operation="union", engine="igl")
    print("union 1")
    new = pymesh.boolean(new, bb_point_mesh_2, operation="union", engine="igl")
    print("union 2")
    new = pymesh.boolean(new, bb_point_mesh_3, operation="union", engine="igl")
    print("union 3")
    new = pymesh.boolean(new, bb_point_mesh_4, operation="union", engine="igl")
    print("union 4")
    new = pymesh.boolean(new, bb_point_mesh_5, operation="union", engine="igl")
    print("union 5")
    new = pymesh.boolean(new, bb_point_mesh_6, operation="union", engine="igl")
    print("union 6")
    new = pymesh.boolean(new, bb_point_mesh_7, operation="union", engine="igl")

    print("union 7")
    return pymesh.boolean(mesh, new, operation="union", engine="igl")



@click.command()
@click.argument("src_file", nargs=1)
@click.argument("dest_file", nargs=1)
def solid(src_file, dest_file):

    mesh = pymesh.meshio.load_mesh(src_file);

    print("start: %d vertexes, %d faces." % (mesh.num_vertices, mesh.num_faces))
    mesh = apply_id(mesh)
    print("solid: %d vertexes, %d faces." % (mesh.num_vertices, mesh.num_faces))

    pymesh.meshio.save_mesh(dest_file, mesh);


def usage(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


if __name__ == "__main__":
    print("make_solid.py running, made with fussy love in Gdansk. <3\n")
    solid()
    sys.exit(0)

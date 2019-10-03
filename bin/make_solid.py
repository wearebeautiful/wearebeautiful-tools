#!/usr/bin/env python

import sys
import os
import copy
from time import time
import numpy as np
from math import fabs, pow, sqrt
from transform import rotate, scale, translate, get_fast_bbox, mirror
from scale_mesh import flip_mesh

import pymesh
import click


BBOX_SHRINK_MM = 1
OUTER_BOX_MM = 15
MAGNET_RADIUS = 30 / 2.0
MAGNET_DEPTH = 3.5
HOOK_BOX_HEIGHT = 10
HOOK_BOX_WIDTH = 5
HOOK_BOX_DEPTH = 10 

# Possible opts:
#   rotate_x, rotate_y, rotate_z,
#   url_top, url_bottom, url_left, url_right,
#   code_top, code_bottom, code_left, code_right):

def apply_id(mesh, opts):

    if opts['rotate_x']:
        mesh = rotate(mesh, (0,0,0), (1, 0, 0), opts['rotate_x'])

    if opts['rotate_y']:
        mesh = rotate(mesh, (0,0,0), (0, 1, 0), opts['rotate_z'])

    if opts['rotate_z']:
        mesh = rotate(mesh, (0,0,0), (0, 0, 1), opts['rotate_z'])

    bbox = get_fast_bbox(mesh)

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
#    outer_box = pymesh.boolean(outer_box, magnet_cup, operation="union", engine="igl")

    hook_center = (inner_box_dims[1][0] - (inner_box_dims[1][0] - inner_box_dims[0][0]) / 8.0, 
                   inner_box_dims[0][1] + (inner_box_dims[1][1] - inner_box_dims[0][1]) / 2.0,
                   inner_box_dims[0][2])

    hook_box = pymesh.generate_box_mesh((hook_center[0] - (HOOK_BOX_WIDTH / 2),
                                         hook_center[1] - (HOOK_BOX_HEIGHT / 2),
                                         hook_center[2] - (HOOK_BOX_DEPTH / 2)),
                                        (hook_center[0] + (HOOK_BOX_WIDTH / 2),
                                         hook_center[1] + (HOOK_BOX_HEIGHT / 2),
                                         hook_center[2] + (HOOK_BOX_DEPTH / 2)))
#    outer_box = pymesh.boolean(outer_box, hook_box, operation="union", engine="igl")

    if 0:
        print("make code")
        code = pymesh.meshio.load_mesh("input/883440VSNN.stl")

        print("rotate")
        code = rotate(code, (0,0,0), (1, 0, 0), 90)
#        code = rotate(code, (0,0,0), (0, 0, 1), 180)

        print("scale")
        cbox = get_fast_bbox(code)
        code_w = cbox[1][0] - cbox[0][0]
        box_w = inner_box_dims[1][0] - inner_box_dims[0][0]
        scale_x = (box_w * .7)  / code_w
        code = scale(code, (scale_x, scale_x, scale_x))

        print("translate")
        cbox = get_fast_bbox(code)
        code_w = cbox[1][0] - cbox[0][0]
        trans_x = (code_w / 2.0) + ((box_w - code_w) / 2.0)
        trans_y = -100
        trans_z = -5
        code = translate(code, (trans_x,trans_y,-trans_z))

        print("glue")
        outer_box = pymesh.boolean(outer_box, code, operation="union", engine="igl")

#        return outer_box

    print("make url")
    url = pymesh.meshio.load_mesh("input/wearebeautiful.info.stl")

    ubox = get_fast_bbox(url)
    url_w = ubox[1][0] - ubox[0][0]
    url_h = ubox[1][1] - ubox[0][1]

    print("rotate")
    if opts['url_left']:
        url = rotate(url, (0,0,0), (0, 1, 0), -90)
        url = rotate(url, (0,0,0), (1, 0, 0), 180)
    elif opts['url_right']:
        url = rotate(url, (0,0,0), (0, 1, 0), -90)
        url = rotate(url, (0,0,0), (0, 0, 1), 180)
        url = rotate(url, (0,0,0), (1, 0, 0), 180)
    elif opts['url_bottom']:
        url = rotate(url, (0,0,0), (0, 1, 0), 90)
        url = rotate(url, (0,0,0), (0, 0, 1), -90)
    elif opts['url_top']:
        url = rotate(url, (0,0,0), (0, 1, 0), 90)
        url = rotate(url, (0,0,0), (0, 0, 1), 90)

    print("scale")
    if opts['url_bottom'] or opts['url_top']:
        box_w = inner_box_dims[1][1] - inner_box_dims[0][1]
    else:
        box_w = inner_box_dims[1][0] - inner_box_dims[0][0]

    scale_f = (box_w * .7)  / url_w
    url = scale(url, (scale_f, scale_f, scale_f))

#    print("translate")
#    ubox = get_fast_bbox(url)
#    trans_x = (url_w / 2.0) + ((box_w - url_w) / 2.0)
#    trans_y = 5 # inner_box_dims[0][1]
#    trans_z = -5 # -(ubox[1][2] - ubox[0][2]) 
#    url = translate(url, (trans_x,trans_y,trans_z))

    print("glue")
    outer_box = pymesh.boolean(outer_box, url, operation="union", engine="igl")
    return outer_box

    print("final subtract")
    return pymesh.boolean(mesh, outer_box, operation="difference", engine="igl")



@click.command()
@click.argument("src_file", nargs=1)
@click.argument("dest_file", nargs=1)
@click.option('--rotate-x', '-rx', default=0, type=int)
@click.option('--rotate-y', '-ry', default=0, type=int)
@click.option('--rotate-z', '-rz', default=0, type=int)
@click.option('--url-top', '-ut', is_flag=True, default=False)
@click.option('--url-bottom', '-ub', is_flag=True, default=False)
@click.option('--url-left', '-ul', is_flag=True, default=False)
@click.option('--url-right', '-ur', is_flag=True, default=False)
@click.option('--url-top', '-ct', is_flag=True, default=False)
@click.option('--code-top', '-ct', is_flag=True, default=False)
@click.option('--code-bottom', '-cb', is_flag=True, default=False)
@click.option('--code-left', '-cl', is_flag=True, default=False)
@click.option('--code-right', '-cr', is_flag=True, default=False)
@click.option('--code-top', '-ct', is_flag=True, default=False)
def solid(src_file, dest_file, **opts):

    if opts['url_top'] and opts['url_bottom']:
        print("Cannot use url_top and url_bottom at the same time. pick one!")
        sys.exit(-1)
    if opts['url_left'] and opts['url_right']:
        print("Cannot use url_left and url_right at the same time. pick one!")
        sys.exit(-1)
    if opts['code_top'] and opts['code_bottom']:
        print("Cannot use code_top and code_bottom at the same time. pick one!")
        sys.exit(-1)
    if opts['code_left'] and opts['code_right']:
        print("Cannot use code_left and code_right at the same time. pick one!")
        sys.exit(-1)

    if not opts['url_top'] and not opts['url_bottom'] and not opts['url_left'] and not opts['url_right']:
        opts['url_top'] = True
    if not opts['code_top'] and not opts['code_bottom'] and not opts['code_left'] and not opts['code_right']:
        opts['code_bottom'] = True

    print(opts)

    mesh = pymesh.meshio.load_mesh(src_file);
    mesh = apply_id(mesh, opts)
    pymesh.meshio.save_mesh(dest_file, mesh);


def usage(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


if __name__ == "__main__":
    print("make_solid.py running, made with fussy love in Gdansk. <3\n")
    solid()
    sys.exit(0)

#!/usr/bin/env python

import sys
import os
import copy
from time import time
import numpy as np
from math import fabs, pow, sqrt
from transform import rotate, scale, translate, get_fast_bbox, mirror
from scale_mesh import flip_mesh
import subprocess
from pylab import imread
from scipy.ndimage import gaussian_filter
from stl_tools import numpy2stl

import pymesh
import click


OUTER_BOX_MM = 15
TEXT_INSET_DEPTH = 1
MAGNET_RADIUS = 30 / 2.0
MAGNET_DEPTH = 3.5
HOOK_BOX_HEIGHT = 10
HOOK_BOX_WIDTH = 5
HOOK_BOX_DEPTH = 10 

LARGE_TEXT_WIDTH = 540
SMALL_TEXT_WIDTH = 370
TEXT_HEIGHT = 70
FONT_FILE = "d-din.bold.ttf"
IMAGE_FILE = "/tmp/text.png"
TEXT_STL_FILE = "/tmp/text.stl"


def make_text_image(text, large=False):

    if large:
        size = "%dx%d" % (LARGE_TEXT_WIDTH, TEXT_HEIGHT)
    else:
        size = "%dx%d" % (SMALL_TEXT_WIDTH, TEXT_HEIGHT)

    try:
        subprocess.run(["convert", "-size",  size, "xc:black", "/tmp/black.png"], check=True)
    except subprocess.CalledProcessError as err:
        print(str(err))
        sys.exit(-1)

    try:
        subprocess.run(["convert", "-pointsize", "64", "-font", FONT_FILE, "-fill", "white", "-draw", 
            'text 10,60 "%s"' % text, "/tmp/black.png", "/tmp/text.png"], check=True)
    except subprocess.CalledProcessError as err:
        print(str(err))
        sys.exit(-1)

    os.unlink("/tmp/black.png")

    return IMAGE_FILE


def make_stl_from_image(image_file):
    print(image_file)
    A = 256 * imread(image_file)
    A = gaussian_filter(A, 1)
    numpy2stl(A, TEXT_STL_FILE, scale=0.25, mask_val=1, solid=True)
    return TEXT_STL_FILE

def make_text_mesh(text, large):

    image = make_text_image(text, large)


    stl = make_stl_from_image(image)
    os.unlink(image)

    text = pymesh.meshio.load_mesh(stl)
    os.unlink(stl)

    return text


def move_text_to_surface(text, inner_box_dims, side, opts, text_scale):

    ubox = get_fast_bbox(text)
    text_w = ubox[1][0] - ubox[0][0]
    text_h = ubox[1][1] - ubox[0][1]

    if side == 'left':
        text = rotate(text, (0,0,0), (0, 1, 0), -90)
        text = rotate(text, (0,0,0), (1, 0, 0), 180)
    elif side == 'right':
        text = rotate(text, (0,0,0), (0, 1, 0), -90)
        text = rotate(text, (0,0,0), (0, 0, 1), 180)
        text = rotate(text, (0,0,0), (1, 0, 0), 180)
    elif side == 'bottom':
        text = rotate(text, (0,0,0), (0, 1, 0), 90)
        text = rotate(text, (0,0,0), (0, 0, 1), -90)
    elif side == 'top':
        text = rotate(text, (0,0,0), (0, 1, 0), 90)
        text = rotate(text, (0,0,0), (0, 0, 1), 90)

    if side == 'bottom' or side == 'top':
        box_w = inner_box_dims[1][1] - inner_box_dims[0][1]
    else:
        box_w = inner_box_dims[1][0] - inner_box_dims[0][0]

    scale_f = (box_w * text_scale)  / text_w
    text = scale(text, (scale_f, scale_f, scale_f))

    ubox = get_fast_bbox(text)
    trans_x = trans_y = trans_z = 0.0

    if side == 'left':
        trans_x = inner_box_dims[1][1] + ubox[1][1] - opts['text_depth']
    elif side == 'right':
        trans_x = -inner_box_dims[1][1]  - ubox[1][1] + opts['text_depth']
    elif side == 'bottom':
        trans_y = -inner_box_dims[1][0]  - ubox[1][0] + opts['text_depth']
    elif side == 'top':
        trans_y = inner_box_dims[1][0]  + ubox[1][0] - opts['text_depth']

    trans_z = (inner_box_dims[0][2] - ubox[0][2]) + opts['z_offset']

    return translate(text, (trans_x,trans_y,trans_z))


def make_solid(mesh, opts):

    print("make solid")

    # perform initial rotation
    if opts['rotate_x']:
        mesh = rotate(mesh, (0,0,0), (1, 0, 0), opts['rotate_x'])

    if opts['rotate_y']:
        mesh = rotate(mesh, (0,0,0), (0, 1, 0), opts['rotate_z'])

    if opts['rotate_z']:
        mesh = rotate(mesh, (0,0,0), (0, 0, 1), opts['rotate_z'])

    # center the surface on the origin
    bbox = get_fast_bbox(mesh)
    width_x = bbox[1][0] - bbox[0][0]
    width_y = bbox[1][1] - bbox[0][1]
    width_z = bbox[1][2] - bbox[0][2]
    trans_x = -((width_x / 2.0) + bbox[0][0])
    trans_y = -((width_y / 2.0) + bbox[0][1])
    trans_z = -((width_z / 2.0) + bbox[0][2])
    mesh = translate(mesh, (trans_y, trans_x, trans_z))
    bbox = get_fast_bbox(mesh)

    bbox = get_fast_bbox(mesh)

    bbox[0][0] += opts['crop']
    bbox[0][1] += opts['crop']

    bbox[1][0] -= opts['crop']
    bbox[1][1] -= opts['crop']

    inner_box_dims = copy.deepcopy(bbox)

    inner_box = pymesh.generate_box_mesh(bbox[0], bbox[1])

    bbox[0][0] -= OUTER_BOX_MM
    bbox[0][1] -= OUTER_BOX_MM
    bbox[0][2] -= OUTER_BOX_MM

    bbox[1][0] += OUTER_BOX_MM
    bbox[1][1] += OUTER_BOX_MM

    print("make modifications")
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


    if opts['url_top']:
        url_side = 'top';
    elif opts['url_bottom']:
        url_side = 'bottom';
    elif opts['url_left']:
        url_side = 'left';
    elif opts['url_right']:
        url_side = 'right';

    if opts['code_top']:
        code_side = 'top';
    elif opts['code_bottom']:
        code_side = 'bottom';
    elif opts['code_left']:
        code_side = 'left';
    elif opts['code_right']:
        code_side = 'right';

    print("make url")
    url = make_text_mesh("wearebeautiful.info", True)
    url = move_text_to_surface(url, inner_box_dims, url_side, opts, opts['url_scale'])
    outer_box = pymesh.boolean(outer_box, url, operation="union", engine="igl")

    print("make code")
    code = make_text_mesh("883440VSNN", False)
    code = move_text_to_surface(code, inner_box_dims, code_side, opts, opts['code_scale'])
    outer_box = pymesh.boolean(outer_box, code, operation="union", engine="igl")

#return outer_box

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
@click.option('--z-offset', '-z', default=2.0, type=float)
@click.option('--code-scale', '-cz', default=.7, type=float)
@click.option('--url-scale', '-uz', default=.7, type=float)
@click.option('--crop', '-c', default=1, type=float)
@click.option('--text-depth', '-', default=.7, type=float)
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

    if (opts['code_top'] and opts['url_top']) or \
        (opts['code_bottom'] and opts['url_bottom']) or \
        (opts['code_left'] and opts['url_left']) or \
        (opts['code_right'] and opts['url_right']): 
        print("Cannot apply code and URL to the same side.")
        sys.exit(-1)


    mesh = pymesh.meshio.load_mesh(src_file);
    mesh = make_solid(mesh, opts)
    pymesh.meshio.save_mesh(dest_file, mesh);


def usage(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


if __name__ == "__main__":
    print("make_solid.py running, made with fussy love in Gdansk. <3\n")
    solid()
    sys.exit(0)

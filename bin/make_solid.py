import sys
import os
import copy
from time import time
import numpy as np
from math import fabs, pow, sqrt
from transform import rotate, scale, translate, get_fast_bbox, mirror, make_3d, center_around_origin, save_mesh
from scale_mesh import flip_mesh
import subprocess
from pylab import imread
from scipy.ndimage import gaussian_filter
from scipy.spatial import Delaunay
from stl_tools import numpy2stl
from edge import create_walls_and_floor

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
SMALL_TEXT_WIDTH = 470
TEXT_HEIGHT = 70
FONT_FILE = "d-din.ttf"
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

    text = center_around_origin(text)

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
    elif side == 'top':
        text = rotate(text, (0,0,0), (0, 1, 0), 90)
        text = rotate(text, (0,0,0), (0, 0, 1), -90)
    elif side == 'bottom':
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
        trans_x = -inner_box_dims[1][1] - ubox[1][1] + opts['text_depth']
    elif side == 'top':
        trans_y = -inner_box_dims[1][0] - ubox[1][0] + opts['text_depth']
    elif side == 'bottom':
        trans_y = inner_box_dims[1][0] + ubox[1][0] - opts['text_depth']

    trans_z = (inner_box_dims[0][2] - ubox[0][2]) + opts['z_offset']

    return translate(text, (trans_x,trans_y,trans_z))


def extrude(mesh, opts):

    bbox = get_fast_bbox(mesh)
    extrude_mm = bbox[0][2] - opts['extrude']

    print("build walls")
    walls, floor = create_walls_and_floor(mesh, opts, extrude_mm)

    # floor
    if opts['floor']:
        if opts['flip_floor']:
            floor = flip_mesh(floor)
#        floor = pymesh.split_long_edges(floor, .2)[0]
#        floor = pymesh.remove_obtuse_triangles(floor)[0]

    # make the walls
    if opts['flip_walls']:
        walls = flip_mesh(walls)
    if opts['debug']:
        save_mesh("walls", walls);

    if opts['debug']:
        save_mesh("cleaned", mesh);

    if opts['floor']:
        mesh = pymesh.merge_meshes([mesh, walls, floor]) 
    else:
        mesh = pymesh.merge_meshes([mesh, walls])
    if opts['debug']:
        save_mesh("merged", mesh);

    return mesh

# TODO: Detect inside out meshes, turn right side in.
#       Make extrude optional
def make_solid(mesh, code, opts):

    print("make solid")

    # perform initial rotation
    if opts['rotate_x']:
        mesh = rotate(mesh, (0,0,0), (1, 0, 0), opts['rotate_x'])

    if opts['rotate_y']:
        mesh = rotate(mesh, (0,0,0), (0, 1, 0), opts['rotate_z'])

    if opts['rotate_z']:
        mesh = rotate(mesh, (0,0,0), (0, 0, 1), opts['rotate_z'])

    if opts['debug']:
        save_mesh("after-orient", mesh);

    mesh = center_around_origin(mesh)

    if not opts['no_extrude']:
        print("extrude ...")
        mesh = extrude(mesh, opts)
        mesh = center_around_origin(mesh)

    if opts['flip_after_extrude']:
        mesh = flip_mesh(mesh)

    if opts['debug']:
        save_mesh("after-extruded", mesh);

    bbox = get_fast_bbox(mesh)

    if opts['crop']:
        bbox[0][0] += opts['crop']
        bbox[0][1] += opts['crop']

        bbox[1][0] -= opts['crop']
        bbox[1][1] -= opts['crop']

    inner_box_dims = copy.deepcopy(bbox)

    inner_box = pymesh.generate_box_mesh(bbox[0], bbox[1])

    bbox[0][0] -= OUTER_BOX_MM
    bbox[0][1] -= OUTER_BOX_MM
    bbox[0][2] -= OUTER_BOX_MM
    # tiny debug fudge to not have two faces intersecting each other
    bbox[0][2] -= .001

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
#    if opts['debug']:
#        save_mesh("modified", outer_box);

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
    code = make_text_mesh(code, False)
    code = move_text_to_surface(code, inner_box_dims, code_side, opts, opts['code_scale'])
    outer_box = pymesh.boolean(outer_box, code, operation="union", engine="igl")

    if opts['debug']:
        save_mesh("before-subtract", outer_box);

    print("final subtract")
    return pymesh.boolean(mesh, outer_box, operation="difference", engine="igl")




# New features
# - Extrude amount
# - Label offset on face (as %)
# - Fix right label depth

@click.command()
@click.argument("code", nargs=1)
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
@click.option('--text-depth', '-td', default=.7, type=float)
@click.option('--extrude', '-e', default=2, type=float)
@click.option('--label-offset', '-o', default=0, type=float)
@click.option('--walls', '-w', is_flag=True, default=True)
@click.option('--floor', '-f', is_flag=True, default=True)
@click.option('--flip-after-extrude', '-fl', is_flag=True, default=False)
@click.option('--flip-walls', '-fw', is_flag=True, default=False)
@click.option('--flip-floor', '-fw', is_flag=True, default=False)
@click.option('--debug', '-d', is_flag=True, default=False)
@click.option('--no-extrude', '-n', is_flag=True, default=False)
def solid(code, src_file, dest_file, **opts):

    if opts['debug']:
        try:
            os.mkdir("debug")
        except FileExistsError:
            pass

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
    mesh = make_solid(mesh, code, opts)
    print("is manifold: ", mesh.is_manifold())
    print("is closed: ", mesh.is_closed())
    pymesh.meshio.save_mesh(dest_file, mesh);
    print("done!")


def usage(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


if __name__ == "__main__":
    print("make_solid.py running, made with fussy love in Gdansk. <3\n")
    solid()
    sys.exit(0)




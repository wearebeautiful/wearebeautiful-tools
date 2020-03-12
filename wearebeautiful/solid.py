import sys
import os
import copy
from time import time
import numpy as np
from math import fabs, pow, sqrt
from wearebeautiful.utils import rotate, scale, translate, get_fast_bbox, make_3d, center_around_origin, save_mesh, flip_mesh
from wearebeautiful.extrude import simple_extrude
import subprocess
from pylab import imread
from scipy.ndimage import gaussian_filter
from stl_tools import numpy2stl

import pymesh


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
FONT_FILE = "font/d-din.ttf"
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
#    os.unlink(stl)

    return text


def move_text_to_surface(text, inner_box_dims, side, opts, text_scale, horiz_offset, vert_offset):

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

    trans_y += horiz_offset
    trans_z = (inner_box_dims[0][2] - ubox[0][2]) + opts['z_offset']
    trans_z += vert_offset

    return translate(text, (trans_x,trans_y,trans_z))


def make_solid_main(mesh, opts):

    mesh = center_around_origin(mesh)

    # perform initial rotation
    if opts['rotate_x']:
        mesh = rotate(mesh, (0,0,0), (1, 0, 0), opts['rotate_x'])

    if opts['rotate_y']:
        mesh = rotate(mesh, (0,0,0), (0, 1, 0), opts['rotate_y'])

    if opts['rotate_z']:
        mesh = rotate(mesh, (0,0,0), (0, 0, 1), opts['rotate_z'])

    mesh = center_around_origin(mesh)

    if opts['debug']:
        save_mesh("after-orient", mesh);

    print("extrude ...")
    bbox = get_fast_bbox(mesh)
    surface_height = (bbox[1][2] - bbox[0][2])
    extrude_mm = surface_height + opts['extrude']
    mesh = simple_extrude(mesh, opts, extrude_mm)
    mesh = center_around_origin(mesh)
    if opts['debug']:
        save_mesh("extruded", mesh);

    return mesh, surface_height


def modify_solid(mesh, surface_height, code, opts):

    bbox = get_fast_bbox(mesh)
    if opts['crop']:
        bbox[0][0] += opts['crop']
        bbox[0][1] += opts['crop']

        bbox[1][0] -= opts['crop']
        bbox[1][1] -= opts['crop']


    inner_box_dims = copy.deepcopy(bbox)

    inner_box = pymesh.generate_box_mesh(bbox[0], bbox[1])
    if opts['debug']:
        save_mesh("inner_box", inner_box);

    bbox[0][0] -= OUTER_BOX_MM
    bbox[0][1] -= OUTER_BOX_MM
    bbox[0][2] -= OUTER_BOX_MM
    # tiny debug fudge to not have two faces intersecting each other
    bbox[0][2] -= .001

    bbox[1][0] += OUTER_BOX_MM
    bbox[1][1] += OUTER_BOX_MM

    bbox[0][2] -= surface_height


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

    if not opts['no_url']:
        print("make url")
        url = make_text_mesh("wearebeautiful.info", True)
        url = move_text_to_surface(url, inner_box_dims, url_side, opts, opts['url_scale'], opts['url_h_offset'], opts['url_v_offset'])
        outer_box = pymesh.boolean(outer_box, url, operation="union", engine="igl")

    if not opts['no_code']:
        print("make code")
        code = make_text_mesh(code, False)
        code = move_text_to_surface(code, inner_box_dims, code_side, opts, opts['code_scale'], opts['code_h_offset'], opts['code_v_offset'])
        outer_box = pymesh.boolean(outer_box, code, operation="union", engine="igl")

    if opts['debug']:
        save_mesh("before-subtract outer_box", outer_box);

    print("final subtract")
    if surface_height:
        mesh = translate(mesh, (0, 0, -surface_height))
    if opts['debug']:
        save_mesh("before-subtract mesh", mesh);
    return pymesh.boolean(mesh, outer_box, operation="difference", engine="igl")


def make_solid(code, src_file, dest_file, opts):
    if opts['debug']:
        try:
            os.mkdir("debug")
        except FileExistsError:
            pass

    if opts['url_top'] and opts['url_bottom']:
        print("Cannot use url_top and url_bottom at the same time. pick one!")
        return False
    if opts['url_left'] and opts['url_right']:
        print("Cannot use url_left and url_right at the same time. pick one!")
        return False
    if opts['code_top'] and opts['code_bottom']:
        print("Cannot use code_top and code_bottom at the same time. pick one!")
        return False
    if opts['code_left'] and opts['code_right']:
        print("Cannot use code_left and code_right at the same time. pick one!")
        return False

    if not opts['url_top'] and not opts['url_bottom'] and not opts['url_left'] and not opts['url_right']:
        opts['url_top'] = True
    if not opts['code_top'] and not opts['code_bottom'] and not opts['code_left'] and not opts['code_right']:
        opts['code_bottom'] = True

#    if (opts['code_top'] and opts['url_top']) or \
#        (opts['code_bottom'] and opts['url_bottom']) or \
#        (opts['code_left'] and opts['url_left']) or \
#        (opts['code_right'] and opts['url_right']): 
#        print("Cannot apply code and URL to the same side.")
#        return False


    mesh = pymesh.meshio.load_mesh(src_file);
    if not opts['solid']:
        mesh, surface_height = make_solid_main(mesh, opts)
    else:
        mesh = center_around_origin(mesh)
        if opts['rotate_x']:
            mesh = rotate(mesh, (0,0,0), (1, 0, 0), opts['rotate_x'])

        if opts['rotate_y']:
            mesh = rotate(mesh, (0,0,0), (0, 1, 0), opts['rotate_y'])

        if opts['rotate_z']:
            mesh = rotate(mesh, (0,0,0), (0, 0, 1), opts['rotate_z'])
        mesh = center_around_origin(mesh)
        surface_height = 0

    mesh = modify_solid(mesh, surface_height, code, opts)
    mesh = center_around_origin(mesh)
    print("is manifold: ", mesh.is_manifold())
    print("is closed: ", mesh.is_closed())
    print("writing %s" % dest_file)
    pymesh.meshio.save_mesh(dest_file, mesh);

    return True

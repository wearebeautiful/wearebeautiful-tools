#!/usr/bin/env python

import sys
sys.path.append("..")

import json
import click
import datetime
import os
import shutil
from zipfile import ZipFile
from tempfile import mkdtemp
from scale_mesh import scale_mesh
from wearebeautiful.bundles import validate_manifest, MAX_SCREENSHOT_SIZE
from wearebeautiful import model_params as param

@click.command()
@click.option('--invert/--no-invert', default=False, help='Flip the normals on the STL file')
@click.argument('lresolution', type=float)
@click.argument('mresolution', type=float)
def main(invert, lresolution, mresolution):

    manifest = os.path.join("/src", param.MANIFEST_FILE)
    surface = os.path.join("/src", param.SURFACE_FILE)
    solid = os.path.join("/src", param.PRINT_FILE)
    screenshot = os.path.join("/src", param.SCREENSHOT_FILE)

    try:
        with open(os.path.join("/src", manifest), "rb") as m:
            j = m.read()
            jmanifest = json.loads(j)
    except json.decoder.JSONDecodeError as err:
        print("Cannot parse manifest file. ", err)
        print("This was the content that was read:")
        print("%s\n" % j) 
        sys.exit(-1)
    except IOError as err:
        print("Cannot read manifest file. IO error.", err)
        sys.exit(-1)

    err = validate_manifest(jmanifest)
    if err:
        print(err)
        sys.exit(-1)

    id = jmanifest['id']

    screenshot_size = os.path.getsize(screenshot)
    if screenshot_size > MAX_SCREENSHOT_SIZE:
        print("Maximum screenshot size is %d kbytes." % (MAX_SCREENSHOT_SIZE / 1024))
        sys.exit(-1)

    tmp_dir = mkdtemp()
    low_res = os.path.join(tmp_dir, "surface-low.stl")
    medium_res = os.path.join(tmp_dir, "surface-medium.stl")

    if not os.path.exists(solid):
        print("Cannot find solid.stl");
        sys.exit(-1)

    if not os.path.exists(surface):
        print("Cannot find surface.stl");
        sys.exit(-1)

    try:
        print("invert mesh", invert)
        scale_mesh(invert, lresolution, surface, low_res)
        scale_mesh(invert, mresolution, surface, medium_res)
    except IOError as err:
        print("Cannot down-scale mesh files. Error: ", err)
        sys.exit(-1)

    try:
        shutil.copy(solid, tmp_dir)
        shutil.copy(surface, tmp_dir)
        shutil.copy(screenshot, tmp_dir)
    except IOError as err:
        print("Cannot copy files. Error: ", err)
        sys.exit(-1)

    dest = os.path.join("/dest", "%s-%s-%s-bundle.zip" % (id, jmanifest['bodypart'], jmanifest['pose']))
    with ZipFile(dest, 'w') as zip:
        zip.write(manifest, arcname="manifest.json")
        zip.write(low_res, arcname="surface-low.stl")
        zip.write(medium_res, arcname="surface-medium.stl")
        zip.write(solid, arcname="solid.stl")
        zip.write(surface, arcname="surface-orig.stl")
        zip.write(screenshot, arcname="screenshot.jpg")

    shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    main();
    sys.exit(-1)

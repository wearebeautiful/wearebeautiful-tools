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
from wearebeautiful.bundles import validate_manifest
from wearebeautiful import model_params as param

@click.command()
@click.argument('lresolution')
@click.argument('mresolution')
def main(lresolution, mresolution):

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
        print("err)
        sys.exit(-1)

    id = jmanifest['id']

    tmp_dir = mkdtemp()
    low_res = os.path.join(tmp_dir, "surface-low.obj")
    medium_res = os.path.join(tmp_dir, "surface-medium.obj")

    if not os.path.exists(solid):
        solid = os.path.splitext(os.path.basename(solid))[0] + ".stl"
        solid = os.path.join("/src", solid)
        print("Could not find solid.obj, trying %s" % solid)
        if not os.path.exists(solid):
            print("Cannot find solid.obj or solid.stl");
            sys.exit(-1)

    if not os.path.exists(surface):
        surface = os.path.splitext(os.path.basename(surface))[0] + ".stl"
        surface = os.path.join("/src", surface)
        print("Could not find surface.obj, trying %s" % surface)
        if not os.path.exists(surface):
            print("Cannot find surface.obj or surface.stl");
            sys.exit(-1)

    try:
        scale_mesh(surface, low_res, float(lresolution))
        scale_mesh(surface, medium_res, float(mresolution))
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

    dest = os.path.join("/dest", "%06d-%s-%s-bundle.zip" % (id, jmanifest['bodypart'], jmanifest['pose']))
    with ZipFile(dest, 'w') as zip:
        zip.write(manifest, arcname="manifest.json")
        zip.write(low_res, arcname="surface-low.obj")
        zip.write(medium_res, arcname="surface-medium.obj")
        zip.write(solid, arcname="solid.obj")
        zip.write(surface, arcname="surface-orig.obj")
        zip.write(screenshot, arcname="screenshot.jpg")

    shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    main();

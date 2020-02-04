import os
import sys
import json
import shutil
from copy import copy
from wearebeautiful.solid import make_solid
from make_solid import default_opts
from wearebeautiful.scale import scale_mesh
from wearebeautiful.manifest import validate_manifest, make_code

def get_dest_paths(mjson, dest_dir):

    code = make_code(manifest=mjson)
    id = mjson['id']
    solid_file = "%s-%s-solid.stl" % (code, mjson["processed"])
    solid_file = os.path.join(dest_dir, id, code, solid_file)
    surface_file = "%s-%s-surface.stl" % (code, mjson["processed"])
    surface_file = os.path.join(dest_dir, id, code, surface_file)
    surface_med_file = "%s-%s-surface-med.stl" % (code, mjson["processed"])
    surface_med_file = os.path.join(dest_dir, id, code, surface_med_file)
    surface_low_file = "%s-%s-surface-low.stl" % (code, mjson["processed"])
    surface_low_file = os.path.join(dest_dir, id, code, surface_low_file)
    manifest_file = "%s-%s-manifest.stl" % (code, mjson["processed"])
    manifest_file = os.path.join(dest_dir, id, code, manifest_file)

    return solid_file, surface_file, surface_med_file, surface_low_file, manifest_file


def process_surface(manifest, surface, dest_dir):

    if not os.path.exists(manifest):
        print("manifest file %s does not exist." % manifest)
        return False

    if not os.path.exists(surface):
        print("surface file %s does not exist." % surface)
        return False

    if not os.path.isdir(dest_dir):
        print("dest dir %s does not exist or is not accessible." % dest_dir)
        return False

    try:
        with open(manifest, "rb") as f:
            mjson = json.loads(str(f.read().decode('utf-8')))
    except IOError as err:
        print("problem reading manifest: ", str(err))
        return False
    except json.decoder.JSONDecodeError as err:
        print("problem decoding manifest: ", str(err))
        return False

    msg = validate_manifest(mjson)
    if msg:
        print("Manifest parse error:")
        print(msg)
        return False

    code = make_code(manifest=mjson)
    solid_file, surface_file, surface_med_file, surface_low_file, manifest_file = get_dest_paths(mjson, dest_dir)

    dest_dir = os.path.join(dest_dir, mjson['id'], code)
    try:
        os.makedirs(dest_dir)
    except FileExistsError:
        pass

    opts = copy(default_opts)
    if 'make_solid_args' in mjson:
        for k in mjson['make_solid_args']:
            opts[k] = mjson['make_solid_args'][k]

    print(opts)
    opts['debug'] = True

    print("create solid: %s" % solid_file)
    if not make_solid(code, surface, solid_file, opts):
        return False

    print("copying %s" % surface)
    shutil.copyfile(surface, surface_file)
    print("copying %s" % manifest)
    shutil.copyfile(manifest, manifest_file)

    print("scaling medium surface %s" % surface_med_file)
    scale_mesh(False, .3, surface, surface_med_file, { 'cleanup' : False })
    print("scaling low surface %s" % surface_low_file)
    scale_mesh(False, .5, surface, surface_low_file, { 'cleanup' : False })

    return True

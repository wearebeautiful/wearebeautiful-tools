import os
import sys
import json
import shutil
import subprocess
from copy import copy
from wearebeautiful.solid import make_solid
from make_solid import default_opts
from wearebeautiful.scale import scale_mesh
from wearebeautiful.manifest import validate_manifest, make_code
import config

def get_dest_paths(mjson, dest_dir):

    code = make_code(manifest=mjson)
    id = mjson['id']
    solid_file = "%s-%s-solid.stl" % (code, mjson["processed"])
    solid_file = os.path.join(dest_dir, solid_file)
    surface_file = "%s-%s-surface.stl" % (code, mjson["processed"])
    surface_file = os.path.join(dest_dir, surface_file)
    surface_med_file = "%s-%s-surface-med.stl" % (code, mjson["processed"])
    surface_med_file = os.path.join(dest_dir, surface_med_file)
    surface_low_file = "%s-%s-surface-low.stl" % (code, mjson["processed"])
    surface_low_file = os.path.join(dest_dir, surface_low_file)
    manifest_file = "%s-%s-manifest.json" % (code, mjson["processed"])
    manifest_file = os.path.join(dest_dir, manifest_file)

    return solid_file, surface_file, surface_med_file, surface_low_file, manifest_file


def process_surface(id, code, force = False):

    processed = 0

    path = os.path.join(config.SURFACE_DIR, id, code)
    manifest = os.path.join(path, "manifest.json")
    if not os.path.exists(manifest):
        print("manifest file %s does not exist." % manifest)
        return False

    surface = os.path.join(path, "surface.stl")
    if not os.path.exists(surface):
        print("surface file %s does not exist." % surface)
        return False

    solid_input = os.path.join(path, "solid.stl")
    is_solid = os.path.exists(solid_input)

    if not os.path.isdir(config.MODEL_DIR):
        print("model dir %s does not exist or is not accessible." % config.MODEL_DIR)
        return False

    if not os.path.isdir(config.MODEL_GIT_DIR):
        print("model git dir %s does not exist or is not accessible." % config.MODEL_DIR)
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

    gen_code = make_code(manifest=mjson)
    if "%s-%s" % (id, code) != gen_code:
        print("Code passed on the command line '%s' and code generated from the manifest.json '%s' do not match!" % (code, gen_code))
        return False

    # set up the correction options for make_solid
    opts = copy(default_opts)
    if 'make_solid_args' in mjson:
        for k in mjson['make_solid_args']:
            opts[k] = mjson['make_solid_args'][k]

    opts['debug'] = True

    # Set up the plain copy destination
    dest_dir = os.path.join(config.MODEL_DIR, mjson['id'], code)
    try:
        os.makedirs(dest_dir)
    except FileExistsError:
        pass
    solid_file, surface_file, surface_med_file, surface_low_file, manifest_file = get_dest_paths(mjson, dest_dir)

    # Set up the compressed copy destination
    comp_dest_dir = os.path.join(config.MODEL_GIT_DIR, mjson['id'], code)
    try:
        os.makedirs(comp_dest_dir)
    except FileExistsError:
        pass
    solid_file_gz, surface_file_gz, surface_med_file_gz, surface_low_file_gz, manifest_file_git = get_dest_paths(mjson, comp_dest_dir)

    # Now do stuff!
    if force or (not os.path.exists(solid_file) or not os.path.exists(solid_file_gz)):
        if is_solid:
            print("apply code and url to solid: %s" % solid_input)
            if not make_solid(gen_code, solid_input, solid_file, opts):
                return False
        else:
            print("create solid: %s" % solid_file)
            if not make_solid(gen_code, surface, solid_file, opts):
                return False
        shutil.copyfile(solid_file, solid_file_gz)
        subprocess.run(["gzip", "-f", solid_file_gz], check=True)
        processed += 1

    try:
        if force or (not os.path.exists(surface_file) or not os.path.exists(surface_file_gz + ".gz")):
            shutil.copyfile(surface, surface_file)
            shutil.copyfile(surface, surface_file_gz)
            subprocess.run(["gzip", "-f", surface_file_gz], check=True)
            processed += 1

        if force or (not os.path.exists(manifest_file) or not os.path.exists(manifest_file_git + ".gz")):
            shutil.copyfile(manifest, manifest_file)
            shutil.copyfile(manifest_file, manifest_file_git)
            processed += 1

        if force or (not os.path.exists(surface_med_file) or not os.path.exists(surface_med_file_gz + ".gz")):
            print("scaling medium surface %s" % surface_med_file)
            scale_mesh(False, .3, surface, surface_med_file, { 'cleanup' : False })
            shutil.copyfile(surface_med_file, surface_med_file_gz)
            subprocess.run(["gzip", "-f", surface_med_file_gz], check=True)
            processed += 1

        if force or (not os.path.exists(surface_low_file) or not os.path.exists(surface_low_file_gz + ".gz")):
            print("scaling low surface %s" % surface_low_file)
            scale_mesh(False, .5, surface, surface_low_file, { 'cleanup' : False })
            shutil.copyfile(surface_low_file, surface_low_file_gz)
            subprocess.run(["gzip", "-f", surface_low_file_gz], check=True)
            processed += 1

    except subprocess.CalledProcessError as err:
        print("Cannot copy files to archives: ", str(err))
        return False
    except IOError as err:
        print("Cannot copy files to archives: ", str(err))
        return False

    if not processed:
        print("Nothing to process, all up to date.")
    else:
        print("Processed %d items." % processed)

    return True

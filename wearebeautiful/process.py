import os
import sys
import json
import shutil
import subprocess
from copy import copy
import pymesh
from wearebeautiful.solid import make_solid
from make_solid import default_opts
from wearebeautiful.scale import scale_mesh
from wearebeautiful.manifest import validate_manifest, make_code
from wearebeautiful.utils import rotate, center_around_origin
import config

DEFAULT_MED_SURFACE_LEN = .3
DEFAULT_LOW_SURFACE_LEN = .5

def center_mesh(filename):
    src_file = os.path.join("/archive", filename)
    mesh = pymesh.meshio.load_mesh(src_file);
    mesh = center_around_origin(mesh)
    pymesh.meshio.save_mesh(src_file, mesh);


def rotate_mesh(filename, rot_x, rot_y, rot_z):
    src_file = os.path.join("/archive", filename)
    mesh = pymesh.meshio.load_mesh(src_file);

    if rot_x:
        mesh = rotate(mesh, (0,0,0), (1, 0, 0), rot_x)

    if rot_y:
        mesh = rotate(mesh, (0,0,0), (0, 1, 0), rot_y)

    if rot_z:
        mesh = rotate(mesh, (0,0,0), (0, 0, 1), rot_z)

    pymesh.meshio.save_mesh(src_file, mesh);


def get_dest_paths(mjson, dest_dir):

    code = make_code(manifest=mjson, force_version=True)
    id = mjson['id']
    solid_file = "%s-solid.stl" % (code)
    solid_file = os.path.join(dest_dir, solid_file)
    surface_file = "%s-surface.stl" % (code)
    surface_file = os.path.join(dest_dir, surface_file)
    surface_med_file = "%s-surface-med.stl" % (code)
    surface_med_file = os.path.join(dest_dir, surface_med_file)
    surface_low_file = "%s-surface-low.stl" % (code)
    surface_low_file = os.path.join(dest_dir, surface_low_file)
    manifest_file = "%s-manifest.json" % (code)
    manifest_file = os.path.join(dest_dir, manifest_file)

    return solid_file, surface_file, surface_med_file, surface_low_file, manifest_file


def process_surface(id, code, version, force = False):

    processed = 0

    if version > 1:
        path = os.path.join(config.SURFACE_DIR, id, code + "-%d" % version)
    else:
        path = os.path.join(config.SURFACE_DIR, id, code)
    print(path)
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
        print("%s: problem reading manifest: %s" % (manifest, str(err)))
        return False
    except json.decoder.JSONDecodeError as err:
        print("%s: problem decoding manifest: %s" % (manifest, str(err)))
        return False

    msg = validate_manifest(mjson)
    if msg:
        print("%s-%s-%d: Manifest parse error:" % (id, code, version))
        print(msg)
        return False

    cmd_code = "%s-%s" % (id, code)
    if mjson['version'] > 1:
        cmd_code += "-%d" % mjson['version']

    gen_code = make_code(manifest=mjson)
    if cmd_code != gen_code:
        print("Code passed on the command line '%s' and code generated from the manifest.json '%s' do not match!" % (cmd_code, gen_code))
        return False

    if version != int(mjson['version']):
        print("Version passed on the command line %d does not match version in manifest.json %d." % (version, int(mjson['version'])))
        return False

    # set up the correction options for make_solid
    opts = copy(default_opts)
    if 'make_solid_args' in mjson:
        for k in mjson['make_solid_args']:
            opts[k] = mjson['make_solid_args'][k]

    opts['debug'] = True
    if 'surface_med_len' not in opts:
        opts['surface_med_len'] = DEFAULT_MED_SURFACE_LEN
    if 'surface_low_len' not in opts:
        opts['surface_low_len'] = DEFAULT_LOW_SURFACE_LEN

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
    if force or (not os.path.exists(solid_file)) or (not os.path.exists(solid_file_gz + ".gz")):
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
        if force or (not os.path.exists(surface_file)) or (not os.path.exists(surface_file_gz + ".gz")):
            shutil.copyfile(surface, surface_file)
            shutil.copyfile(surface, surface_file_gz)
            subprocess.run(["gzip", "-f", surface_file_gz], check=True)
            processed += 1

        if force or (not os.path.exists(manifest_file) or not os.path.exists(manifest_file_git)):
            shutil.copyfile(manifest, manifest_file)
            shutil.copyfile(manifest_file, manifest_file_git)
            processed += 1

        if force or (not os.path.exists(surface_med_file)) or (not os.path.exists(surface_med_file_gz + ".gz")):
            print("scaling medium surface %s" % surface_med_file)
            scale_mesh(False, opts['surface_med_len'], surface, surface_med_file, { 'cleanup' : False })
            shutil.copyfile(surface_med_file, surface_med_file_gz)
            subprocess.run(["gzip", "-f", surface_med_file_gz], check=True)
            processed += 1

        if force or (not os.path.exists(surface_low_file)) or (not os.path.exists(surface_low_file_gz + ".gz")):
            print("scaling low surface %s" % surface_low_file)
            scale_mesh(False, opts['surface_low_len'], surface, surface_low_file, { 'cleanup' : False })
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
        print("%s-%s Nothing to process, all up to date." % (id, code))
    else:
        print("%s-%s Processed %d items." % (id, code, processed))

    return True

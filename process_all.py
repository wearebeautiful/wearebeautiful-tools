import os
import sys
import json
import shutil
import click
from wearebeautiful.solid import make_solid
from make_solid import default_opts
from wearebeautiful.scale import scale_mesh
from wearebeautiful.manifest import validate_manifest, make_code
from wearebeautiful.process import process_surface, get_dest_paths

surface_dir = "/archive/surfaces ready for processing"
model_dir = "/archive/model-archive"


@click.command()
@click.option('--force', '-f', is_flag=True, default=False)
def process_all(force):

    if not os.path.isdir(surface_dir):
        print("surface dir %s does not exist or is not accessible." % surface_dir)
        sys.exit(-1)

    if not os.path.isdir(model_dir):
        print("model dir %s does not exist or is not accessible." % model_dir)
        sys.exit(-1)

    for dir in os.listdir(surface_dir):
        if dir in ['.','..']:
            continue

        full_path = os.path.join(surface_dir, dir)
        if not os.path.isdir(full_path):
            continue

        if len(dir) != 6 or not dir.isdigit():
            continue

        process_human_model_dir(full_path, force)


def process_human_model_dir(human_model_dir, force):

    for dir in os.listdir(human_model_dir):
        if dir in ['.','..']:
            continue

        if len(dir) != 4:
            continue

        full_path = os.path.join(human_model_dir, dir)
        print("examine %s:" % full_path)
        process_human_model(full_path, force)


def process_human_model(human_model_dir, force):

    manifest_file = None
    surface_file = None
    for filename in os.listdir(human_model_dir):
        if filename in ['.','..']:
            continue

        if filename.endswith(".json"):
            manifest_file = filename
   
        if filename.endswith(".stl"):
            surface_file = filename

    if not manifest_file:
        print("  Could not find manifest file in %s. skipping." % human_model_dir)
        return
    manifest_file = os.path.join(human_model_dir, manifest_file)

    if not surface_file:
        print("  Could not find surface file in %s. skipping." % human_model_dir)
        return
    surface_file = os.path.join(human_model_dir, surface_file)

    print("  process %s %s" % (manifest_file, surface_file))
    try:
        with open(manifest_file, "rb") as f:
            mjson = json.loads(str(f.read().decode('utf-8')))
    except IOError as err:
        print("  problem reading manifest: ", str(err))
        sys.exit(-1)
    except json.decoder.JSONDecodeError as err:
        print("  problem decoding manifest: ", str(err))
        sys.exit(-1)

    msg = validate_manifest(mjson)
    if msg:
        print("  Manifest parse error:")
        print("  " + msg)
        sys.exit(-1)

    make_solid = mjson.get('make-solid-args', "")
    if not make_solid and mjson['body_part'] not in ['vulva', 'penis']:
        print("  For non-vulva, non-penis models, please fill out make-solid-args in manifest.json for %s" % human_model_dir)
        return

    paths = get_dest_paths(mjson, model_dir)
    complete = True
    for path in paths:
        if not os.path.exists(path):
            complete = False

    if not complete or force:
        if process_surface(manifest_file, surface_file, model_dir):
            print("  process surface complete.")
        else:
            print("  process surface failed. :(")
    else:
        print("  complete, skipping")


def usage(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))



if __name__ == "__main__":
    print("process_all.py running, made with high quality fussiness in Barcelona. #fuckbrexit <3\n")
    process_all()
    sys.exit(0)

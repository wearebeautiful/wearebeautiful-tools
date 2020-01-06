import os
import sys
import json
import shutil
import click
from wearebeautiful.solid import make_solid
from make_solid import default_opts
from wearebeautiful.scale import scale_mesh
from wearebeautiful.manifest import validate_manifest, make_code

@click.command()
@click.argument("manifest", nargs=1)
@click.argument("surface", nargs=1)
@click.argument("dest_dir", nargs=1)
def process_surface(manifest, surface, dest_dir):

    if not os.path.exists(manifest):
        print("manifest file %s does not exist." % manifest)
        sys.exit(-1)

    if not os.path.exists(surface):
        print("surface file %s does not exist." % surface)
        sys.exit(-1)

    if not os.path.isdir(dest_dir):
        print("dest dir %s does not exist or is not accessible." % dest_dir)
        sys.exit(-1)

    try:
        with open(manifest, "rb") as f:
            mjson = json.loads(str(f.read().decode('utf-8')))
    except IOError as err:
        print("problem reading manifest: ", str(err))
        sys.exit(-1)
    except json.decoder.JSONDecodeError as err:
        print("problem decoding manifest: ", str(err))
        sys.exit(-1)

    msg = validate_manifest(mjson)
    if msg:
        print("Manifest parse error:")
        print(msg)
        sys.exit(-1)

    code = make_code(manifest=mjson)
    dest_dir = os.path.join(dest_dir, code)
    try:
        os.makedirs(dest_dir)
    except FileExistsError:
        pass

    solid_file = "%s-%s-solid.stl" % (code, mjson["processed"])
    solid_file = os.path.join(dest_dir, solid_file)
    surface_med_file = "%s-%s-surface-med.stl" % (code, mjson["processed"])
    surface_med_file = os.path.join(dest_dir, surface_med_file)
    surface_low_file = "%s-%s-surface-low.stl" % (code, mjson["processed"])
    surface_low_file = os.path.join(dest_dir, surface_low_file)

    print("create solid: %s" % solid_file)
    make_solid(code, surface, solid_file, default_opts)

    print("copying %s" % surface)
    shutil.copyfile(surface, os.path.join(dest_dir, os.path.basename(surface)))
    print("copying %s" % manifest)
    shutil.copyfile(manifest, os.path.join(dest_dir, os.path.basename(manifest)))

    print("scaling medium surface %s" % surface_med_file)
    scale_mesh(False, .3, surface, surface_med_file, { 'cleanup' : False })
    print("scaling low surface %s" % surface_low_file)
    scale_mesh(False, .5, surface, surface_low_file, { 'cleanup' : False })


def usage(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))



if __name__ == "__main__":
    print("process_surface.py running, made with high quality love in Barcelona. <3\n")
    process_surface()
    sys.exit(0)

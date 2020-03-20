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
import config


@click.command()
@click.option('--force', '-f', is_flag=True, default=False)
def process_all(force):

    if not os.path.isdir(config.SURFACE_DIR):
        print("surface dir %s does not exist or is not accessible." % config.SURFACE_DIR)
        sys.exit(-1)

    if not os.path.isdir(config.MODEL_DIR):
        print("model dir %s does not exist or is not accessible." % config.MODEL_DIR)
        sys.exit(-1)

    for dir in os.listdir(config.SURFACE_DIR):
        if dir in ['.','..']:
            continue

        full_path = os.path.join(config.SURFACE_DIR, dir)
        if not os.path.isdir(full_path):
            continue

        if len(dir) != 6 or not dir.isdigit():
            continue

        process_human_model_dir(dir, full_path, force)


def process_human_model_dir(id, human_model_dir, force):

    for dir in os.listdir(human_model_dir):
        if dir in ['.','..']:
            continue

        if len(dir) != 4:
            continue

        full_path = os.path.join(human_model_dir, dir)
        process_surface(id, dir)



def usage(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))



if __name__ == "__main__":
    print("process_all.py running, made with high quality fussiness in Barcelona. #fuckbrexit <3\n")
    process_all()
    sys.exit(0)

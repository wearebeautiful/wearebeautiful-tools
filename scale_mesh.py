#!/usr/bin/env python3

from wearebeautiful.scale import scale_mesh
import click

@click.command()
@click.option('--cleanup', default=False, help='Clean the mesh before scaling')
@click.option('--invert/--no-invert', default=False, help='Flip the normals on the STL file')
@click.argument("len", nargs=1, type=float)
@click.argument("in_file", nargs=1)
@click.argument("out_file", nargs=1)
def scale(invert, len, in_file, out_file):
    scale_mesh(invert, len, in_file, out_file)


def usage(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


if __name__ == "__main__":
    print("scale_mesh.py running, making STL files. <3\n")
    scale()
    sys.exit(0)

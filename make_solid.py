import click
from wearebeautiful.solid import make_solid

@click.command()
@click.argument("code", nargs=1)
@click.argument("src_file", nargs=1)
@click.argument("dest_file", nargs=1)
@click.option('--rotate-x', '-rx', default=0, type=int)
@click.option('--rotate-y', '-ry', default=0, type=int)
@click.option('--rotate-z', '-rz', default=0, type=int)
@click.option('--url-top', '-ut', is_flag=True, default=False)
@click.option('--url-bottom', '-ub', is_flag=True, default=False)
@click.option('--url-left', '-ul', is_flag=True, default=False)
@click.option('--url-right', '-ur', is_flag=True, default=False)
@click.option('--url-top', '-ct', is_flag=True, default=False)
@click.option('--code-top', '-ct', is_flag=True, default=False)
@click.option('--code-bottom', '-cb', is_flag=True, default=False)
@click.option('--code-left', '-cl', is_flag=True, default=False)
@click.option('--code-right', '-cr', is_flag=True, default=False)
@click.option('--code-top', '-ct', is_flag=True, default=False)
@click.option('--z-offset', '-z', default=2.0, type=float)
@click.option('--code-v-offset', '-cvo', default=0.0, type=float)
@click.option('--url-v-offset', '-uvo', default=0.0, type=float)
@click.option('--code-h-offset', '-cvo', default=0.0, type=float)
@click.option('--url-h-offset', '-uvo', default=0.0, type=float)
@click.option('--code-scale', '-cz', default=.7, type=float)
@click.option('--url-scale', '-uz', default=.7, type=float)
@click.option('--crop', '-c', default=1, type=float)
@click.option('--text-depth', '-td', default=1, type=float)
@click.option('--extrude', '-e', default=2, type=float)
@click.option('--label-offset', '-o', default=0, type=float)
@click.option('--walls', '-w', is_flag=True, default=True)
@click.option('--flip-walls', '-w', is_flag=True, default=True)
@click.option('--floor', '-f', is_flag=True, default=True)
@click.option('--debug', '-d', is_flag=True, default=False)
@click.option('--no-extrude', '-n', is_flag=True, default=False)
@click.option('--no-code', '-n', is_flag=True, default=False)
@click.option('--no-url', '-n', is_flag=True, default=False)
def solid(code, src_file, dest_file, **opts):
    make_solid(code, src_file, dest_file, opts)


def usage(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


if __name__ == "__main__":
    print("make_solid.py running, made with fussy love in Gdansk. <3\n")
    solid()
    sys.exit(0)

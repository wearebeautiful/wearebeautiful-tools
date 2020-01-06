import click
from wearebeautiful.solid import make_solid

default_opts = {
    'rotate_x' : 0,
    'rotate_y' : 0,
    'rotate_z' : 0,
    'url_top' : False,
    'url_bottom' : False,
    'url_left' : False,
    'url_right' : False,
    'url_top' : False,
    'code_top' : False,
    'code_bottom' : False,
    'code_left' : False,
    'code_right' : False,
    'code_top' : False,
    'z_offset' : 2.0,
    'code_v_offset' : 0.0,
    'url_v_offset' : 0.0,
    'code_h_offset' : 0.0,
    'url_h_offset' : 0.0,
    'code_scale' : .7,
    'url_scale' : .7,
    'crop' : 1.0,
    'text_depth' : 1.0,
    'extrude' : 2.0,
    'label_offset' : 0,
    'walls' : True,
    'flip_walls' : True,
    'floor' : True,
    'debug' : False,
    'no_extrude' : False,
    'no_code' : False,
    'no_url' : False,
}
@click.command()
@click.argument("code", nargs=1)
@click.argument("src_file", nargs=1)
@click.argument("dest_file", nargs=1)
@click.option('--rotate-x', '-rx', default=default_opts['rotate_x'], type=int)
@click.option('--rotate-y', '-ry', default=default_opts['rotate_y'], type=int)
@click.option('--rotate-z', '-rz', default=default_opts['rotate_z'], type=int)
@click.option('--url-top', '-ut', is_flag=True, default=default_opts['url_top'])
@click.option('--url-bottom', '-ub', is_flag=True, default=default_opts['url_bottom'])
@click.option('--url-left', '-ul', is_flag=True, default=default_opts['url_left'])
@click.option('--url-right', '-ur', is_flag=True, default=default_opts['url_right'])
@click.option('--url-top', '-ct', is_flag=True, default=default_opts['url_top'])
@click.option('--code-top', '-ct', is_flag=True, default=default_opts['code_top'])
@click.option('--code-bottom', '-cb', is_flag=True, default=default_opts['code_bottom'])
@click.option('--code-left', '-cl', is_flag=True, default=default_opts['code_left'])
@click.option('--code-right', '-cr', is_flag=True, default=default_opts['code_right'])
@click.option('--code-top', '-ct', is_flag=True, default=default_opts['code_top'])
@click.option('--z-offset', '-z', default=default_opts['z_offset'], type=float)
@click.option('--code-v-offset', '-cvo', default=default_opts['code_v_offset'], type=float)
@click.option('--url-v-offset', '-uvo', default=default_opts['url_v_offset'], type=float)
@click.option('--code-h-offset', '-cvo', default=default_opts['code_h_offset'], type=float)
@click.option('--url-h-offset', '-uvo', default=default_opts['url_h_offset'], type=float)
@click.option('--code-scale', '-cz', default=default_opts['code_scale'], type=float)
@click.option('--url-scale', '-uz', default=default_opts['url_scale'], type=float)
@click.option('--crop', '-c', default=default_opts['crop'], type=float)
@click.option('--text-depth', '-td', default=default_opts['text_depth'], type=float)
@click.option('--extrude', '-e', default=default_opts['extrude'], type=float)
@click.option('--label-offset', '-o', default=default_opts['label_offset'], type=float)
@click.option('--walls', '-w', is_flag=True, default=default_opts['walls'])
@click.option('--flip-walls', '-w', is_flag=True, default=default_opts['flip_walls'])
@click.option('--floor', '-f', is_flag=True, default=default_opts['floor'])
@click.option('--debug', '-d', is_flag=True, default=default_opts['debug'])
@click.option('--no-extrude', '-n', is_flag=True, default=default_opts['no_extrude'])
@click.option('--no-code', '-n', is_flag=True, default=default_opts['no_code'])
@click.option('--no-url', '-n', is_flag=True, default=default_opts['no_url'])
def solid(code, src_file, dest_file, **opts):
    make_solid(code, src_file, dest_file, opts)


def usage(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


if __name__ == "__main__":
    print("make_solid.py running, made with fussy love in Gdansk. <3\n")
    solid()
    sys.exit(0)

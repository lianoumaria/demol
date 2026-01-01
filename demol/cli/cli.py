import click
from demol.lang import build_model
from demol.transformations import m2t_device_svg, m2t_rpi
import os
from demol.definitions import REPO_PATH

@click.group("demol")
@click.pass_context
def cli(ctx):
   """An example CLI for interfacing with a document"""
   pass


@cli.command("validate")
@click.argument("model_filepath")
@click.pass_context
def validate(ctx, model_filepath):
    print(f'[*] Running validation for model {model_filepath}')
    model = build_model(model_filepath)
    if model:
        print(f'[*] Validation passed!')


@cli.command("gen")
@click.argument("generator")
@click.argument("model_filepath")
@click.pass_context
def gen(ctx, generator, model_filepath):
    if generator == 'pi':
        print(f'[*] Running Generator [RPI] for model {model_filepath}')
        #out_dir = os.path.join(REPO_PATH, "output", "rpi")
        out_dir = "output/rpi"
        print(f'[*] Output directory: {out_dir}')
        # Pass the model file path (str) — transformer expects a path, it builds the model internally
        m2t_rpi(model_filepath, out_dir)
    elif generator == 'json':
        print(f'[*] Running Generator [JSON] for model {model_filepath}')
        model = build_model(model_filepath)
    elif generator == 'svg':
        print(f'[*] Running Generator [SVG] for model {model_filepath}')
        model = build_model(model_filepath)
        m2t_device_svg(model)
    elif generator == 'src':
        ## TODO: Integrate raspi and riot code generation
        print(f'[*] Running Generator [Source] for model {model_filepath}')
        pass
    else:
        return


def main():
   cli(prog_name="demol")


if __name__ == '__main__':
   main()

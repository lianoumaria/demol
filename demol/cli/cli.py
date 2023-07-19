import click
from demol.lang import build_model
from demol.transformations import device_to_plantuml


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
    if generator == 'plantuml':
        print(f'[*] Running Generator [PlanUML] for model {model_filepath}')
        model = build_model(model_filepath)
        a = device_to_plantuml(model)
    else:
        return


def main():
   cli(prog_name="demol")


if __name__ == '__main__':
   main()

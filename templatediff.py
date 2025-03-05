#!/usr/bin/env python3
import pathlib
import subprocess
from typing import Generator, Optional, Sequence, Union

import click


THIS_DIR = pathlib.Path(__file__).parent

ARGUS_TEMPLATES = pathlib.Path("src/argus/htmx/templates")
GEANT_TEMPLATES = pathlib.Path("src/geant_argus/geant_argus/templates")


def get_template_names(path: pathlib.Path):
    all_templates = path.rglob("*.html")
    return set(str(t.relative_to(path)) for t in all_templates)


def execute(command: Sequence[str], cwd: Union[str, pathlib.PurePath]) -> str:
    try:
        result = subprocess.run(command, check=True, capture_output=True, cwd=str(cwd), text=True)
        return result.stdout

    except subprocess.CalledProcessError as error:
        status = error.returncode
        raise RuntimeError(
            f'Command {command} returned {status}: """{error.stderr}""".'
        ) from error


def get_changed_files(
    argus_path: pathlib.Path, diff_spec: Optional[str] = ""
) -> Generator[pathlib.Path, None, None]:
    command = ["git", "diff", "--name-only"]
    if diff_spec:
        command.append(diff_spec)
    result = execute(command, cwd=argus_path)
    return (pathlib.Path(p) for p in result.split("\n") if p)


@click.command
@click.argument("argus_path", type=click.Path(file_okay=False, exists=True, dir_okay=True))
@click.argument("diff_spec", default="")
def cli(argus_path: pathlib.Path, diff_spec: str):
    """Helper tool for identifying Argus templates that have been changed upstream (in Argus
    server). Point this tool to a local Argus git checkout located in ARGUS_PATH and supply a
    `git diff` specifier DIFF_SPEC, such as "HEAD^" or "v1.31.0..v1.32.0". This tool will determine
    which argus.htmx templates have changed and will output a list of those templates that are
    overridden in geant-argus. When not supplying DIFF_SPEC, this tool will fall back to a
    comparison of the working tree and the local repository, just like `git diff` without
    arguments.
    """
    changed_template_names = {
        str(p.relative_to(ARGUS_TEMPLATES))
        for p in get_changed_files(argus_path, diff_spec)
        if p.is_relative_to(ARGUS_TEMPLATES)
    }
    our_templates = get_template_names(THIS_DIR / GEANT_TEMPLATES)
    changed_overridden_templates = changed_template_names & our_templates

    if not changed_overridden_templates:
        click.echo("There are no changed templates that are overridden by geant-argus")
        return

    click.echo(
        f"Please check the following {len(changed_overridden_templates)} overridden"
        " templates that have changed upstream:\n",
        err=True,
    )
    click.echo("\n".join(sorted(changed_overridden_templates)))


if __name__ == "__main__":
    cli()

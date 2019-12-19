import sys
import concurrent.futures

import click
import tqdm
import pathlib
import importlib
import typing
import re

from typing import Optional, Iterator, Pattern, Type
from .core import ASTReplacer, CantParseException


class RegexParamType(click.ParamType):
    name = "regex-pattern"

    def convert(
        self,
        value: str,
        param: Optional[click.Parameter] = None,
        ctx: Optional[click.Context] = None,
    ) -> Pattern:
        return re.compile(value)


@click.group()
@click.option("-i", "--import", "import_modules", help="", multiple=True)
@click.option(
    "--regex",
    type=RegexParamType(),
    help="supply an optional regular expression to limit which converters to run.",
)
@click.pass_context
def cli(ctx, import_modules, regex):
    # ensure that ctx.obj exists and is a dict
    ctx.ensure_object(dict)
    for module in import_modules:
        importlib.import_module(module)


@cli.command()
@click.argument(
    "path", type=click.types.Path(exists=True, writable=True, resolve_path=True)
)
@click.option("--ncores", type=int, default=4)
@click.pass_context
def run(ctx, path, ncores):
    path = pathlib.Path(path)
    if path.is_dir():
        paths = list(path.rglob("*.py"))
    else:
        paths = [path]

    import distributed

    with distributed.Client(n_workers=ncores) as client:
        print(client)
        futures = {}
        for p in tqdm.tqdm(sorted(paths), desc="Creating tasks"):
            fut = client.submit(run_converters_on_file, p)
            futures[fut] = p

        progress_iterator = tqdm.tqdm(desc="Scanning :", total=len(futures), miniters=1)
        all_changed = set()
        for resolved_fut in distributed.as_completed(futures):
            path = futures[resolved_fut]
            progress_iterator.update(1)
            progress_iterator.set_description(f"Scanning: {path}")
            try:
                changed = resolved_fut.result()
                if changed:
                    all_changed.add(path)
            except CantParseException as e:
                print(f"Can't parse {path}", file=sys.stderr)
        progress_iterator.close()

        if len(all_changed):
            print("Changed the following files:")
            for path in sorted(all_changed):
                print(f"    {path}")


@cli.command()
@click.pass_context
def available(ctx):
    for klass in discover_converters(ctx.obj.get("REGEX")):
        print(f"{klass.name()}")


def discover_converters(filter_regex: Optional[Pattern]) -> Iterator[Type[ASTReplacer]]:
    for klass in ASTReplacer.__subclasses__():
        if filter_regex and not filter_regex.match(klass.name()):
            continue
        yield klass


def run_converters_on_file(file: pathlib.Path, filter_regex=None):
    code = file.read_text(encoding="utf-8")
    original_code = code

    for klass in discover_converters(filter_regex):
        converter = klass()  # type: ignore
        try:
            code = converter.transform_code(code)
        except CantParseException as e:
            # If we cannot parse the file, just fail
            raise

        if code != original_code:
            file.write_text(code)

    return code != original_code


if __name__ == "__main__":
    cli()

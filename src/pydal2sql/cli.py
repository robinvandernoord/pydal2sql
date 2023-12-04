"""
Create the Typer cli.
"""

import sys
from typing import Optional

import typer
from configuraptor import Singleton
from pydal2sql_core.cli_support import core_alter, core_create
from rich import print
from typing_extensions import Never

from .__about__ import __version__
from .typer_support import (
    DEFAULT_VERBOSITY,
    IS_DEBUG,
    ApplicationState,
    Verbosity,
    with_exit_code,
)
from .types import DBType_Option, OptionalArgument, OutputFormat_Option, Tables_Option

app = typer.Typer(
    no_args_is_help=True,
)
state = ApplicationState()


def info(*args: str) -> None:  # pragma: no cover
    """
    'print' but with blue text.
    """
    print(f"[blue]{' '.join(args)}[/blue]", file=sys.stderr)


def warn(*args: str) -> None:  # pragma: no cover
    """
    'print' but with yellow text.
    """
    print(f"[yellow]{' '.join(args)}[/yellow]", file=sys.stderr)


def danger(*args: str) -> None:  # pragma: no cover
    """
    'print' but with red text.
    """
    print(f"[red]{' '.join(args)}[/red]", file=sys.stderr)


@app.command()
@with_exit_code(hide_tb=not IS_DEBUG)
def create(
    filename: OptionalArgument[str] = None,
    tables: Tables_Option = None,
    db_type: DBType_Option = None,
    dialect: DBType_Option = None,
    magic: Optional[bool] = None,
    noop: Optional[bool] = None,
    function: Optional[str] = None,
    output_format: OutputFormat_Option = None,
    output_file: Optional[str] = None,
) -> bool:
    """
    Build the CREATE statements for one or more pydal/typedal tables.

    Todo:
        more docs

    Examples:
        pydal2sql create models.py
        cat models.py | pydal2sql
        pydal2sql # output from stdin
    """
    dialect = db_type.value if db_type else dialect.value if dialect else None


    config = state.update_config(
        magic=magic,
        noop=noop,
        tables=tables,
        function=function,
        format=output_format,
        input=filename,
        output=output_file,
    ).update(dialect=dialect, _allow_none=True)

    if core_create(
        filename=config.input,
        db_type=config.db_type,
        tables=config.tables,
        verbose=state.verbosity > Verbosity.normal,
        noop=config.noop,
        magic=config.magic,
        function=config.function,
        output_format=config.format,
        output_file=config.output,
    ):
        print("[green] success! [/green]", file=sys.stderr)
        return True
    else:
        print("[red] create failed! [/red]", file=sys.stderr)
        return False


@app.command()
@with_exit_code(hide_tb=not IS_DEBUG)
def alter(
    filename_before: OptionalArgument[str] = None,
    filename_after: OptionalArgument[str] = None,
    db_type: DBType_Option = None,
    dialect: DBType_Option = None,
    tables: Tables_Option = None,
    magic: Optional[bool] = None,
    noop: Optional[bool] = None,
    function: Optional[str] = None,
    output_format: OutputFormat_Option = None,
    output_file: Optional[str] = None,
) -> bool:
    """
    Create the migration statements from one state to the other, by writing CREATE, ALTER and DROP statements.

    Todo:
        docs

    Examples:
        > pydal2sql alter @b3f24091a9201d6 examples/magic.py
        compare magic.py at commit b3f... to current (= as in workdir).

        > pydal2sql alter examples/magic.py@@b3f24091a9201d6 examples/magic_after_rename.py@latest
        compare magic.py (which was renamed to magic_after_rename.py),
            at a specific commit to the latest version in git (ignore workdir version).
    """
    dialect = db_type.value if db_type else dialect.value if dialect else None

    config = state.update_config(
        magic=magic,
        noop=noop,
        tables=tables,
        function=function,
        format=output_format,
        input=filename_before,
        output=output_file,
    ).update(dialect=dialect, _allow_none=True)

    if core_alter(
        config.input,
        filename_after or config.input,
        db_type=config.db_type,
        tables=config.tables,
        verbose=state.verbosity > Verbosity.normal,
        noop=config.noop,
        magic=config.magic,
        function=config.function,
        output_format=config.format,
        output_file=config.output,
    ):
        print("[green] success! [/green]", file=sys.stderr)
        return True
    else:
        print("[red] alter failed! [/red]", file=sys.stderr)
        return False


def show_config_callback() -> Never:
    """
    --show-config requested!
    """
    print(state)
    raise typer.Exit(0)


def version_callback() -> Never:
    """
    --version requested!
    """
    print(f"pydal2sql Version: {__version__}")

    raise typer.Exit(0)


@app.callback(invoke_without_command=True)
def main(
    _: typer.Context,
    config: str = None,
    verbosity: Verbosity = DEFAULT_VERBOSITY,
    # stops the program:
    show_config: bool = False,
    version: bool = False,
) -> None:
    """
    This script can be used to generate the create or alter sql from pydal or typedal.
    """
    if state.config:
        # if a config already exists, it's outdated, so we clear it.
        # only really applicable in Pytest scenarios where multiple commands are executed after eachother
        Singleton.clear(state.config)

    state.load_config(config_file=config, verbosity=verbosity)

    if show_config:
        show_config_callback()
    elif version:
        version_callback()
    # else: just continue

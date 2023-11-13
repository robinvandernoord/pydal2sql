import sys
import typing
from typing import Annotated, Optional

import typer
from configuraptor import Singleton
from pydal2sql_core import get_typing_args
from pydal2sql_core.cli_support import core_alter, core_create
from pydal2sql_core.types import DEFAULT_OUTPUT_FORMAT, SUPPORTED_OUTPUT_FORMATS
from rich import print
from typer import Argument
from typing_extensions import Never

from .__about__ import __version__
from .typer_support import (
    DEFAULT_VERBOSITY,
    IS_DEBUG,
    ApplicationState,
    DB_Types,
    Verbosity,
    with_exit_code,
)

## type fuckery:
T = typing.TypeVar("T")

OptionalArgument = Annotated[Optional[T], Argument()]
# usage: (myparam: OptionalArgument[some_type])

OptionalOption = Annotated[Optional[T], typer.Option()]
# usage: (myparam: OptionalOption[some_type])

DBType_Option = Annotated[DB_Types, typer.Option("--db-type", "--dialect", "-d")]

Tables_Option = Annotated[
    Optional[list[str]],
    typer.Option("--table", "--tables", "-t", help="One or more table names, default is all tables."),
]

OutputFormat_Option = Annotated[
    # Optional[SUPPORTED_OUTPUT_FORMATS],
    Optional[str],
    typer.Option("--format", "--fmt", help=f"One of {get_typing_args(SUPPORTED_OUTPUT_FORMATS)}"),
]

### end typing stuff, start app:

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
    magic: Optional[bool] = None,
    noop: Optional[bool] = None,
    function: Optional[str] = None,
    output_format: OutputFormat_Option = DEFAULT_OUTPUT_FORMAT,
    output_file: Optional[str] = None,
) -> bool:
    """
    todo: docs

    Examples:
        pydal2sql create models.py
        cat models.py | pydal2sql
        pydal2sql # output from stdin
    """
    config = state.update_config(
        magic=magic, noop=noop, tables=tables, db_type=db_type.value if db_type else None, function=function
    )

    if core_create(
        filename=filename,
        db_type=config.db_type,
        tables=config.tables,
        verbose=state.verbosity > Verbosity.normal,
        noop=config.noop,
        magic=config.magic,
        function=config.function,
        output_format=typing.cast(SUPPORTED_OUTPUT_FORMATS, output_format),
        output_file=output_file,
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
    tables: Tables_Option = None,
    magic: Optional[bool] = None,
    noop: Optional[bool] = None,
    function: Optional[str] = None,
    output_format: OutputFormat_Option = DEFAULT_OUTPUT_FORMAT,
    output_file: Optional[str] = None,
) -> bool:
    """
    Todo: docs

    Examples:
        > pydal2sql alter @b3f24091a9201d6 examples/magic.py
        compare magic.py at commit b3f... to current (= as in workdir).

        > pydal2sql alter examples/magic.py@@b3f24091a9201d6 examples/magic_after_rename.py@latest
        compare magic.py (which was renamed to magic_after_rename.py),
            at a specific commit to the latest version in git (ignore workdir version).

    Todo:
        alter myfile.py # only one arg
        # = alter myfile.py@latest myfile.py@current
        # != alter myfile.py - # with - for cli
        # != alter - myfile.py
    """
    config = state.update_config(
        magic=magic, noop=noop, tables=tables, db_type=db_type.value if db_type else None, function=function
    )

    if core_alter(
        filename_before,
        filename_after,
        db_type=config.db_type,
        tables=config.tables,
        verbose=state.verbosity > Verbosity.normal,
        noop=config.noop,
        magic=config.magic,
        function=config.function,
        output_format=typing.cast(SUPPORTED_OUTPUT_FORMATS, output_format),
        output_file=output_file,
    ):
        print("[green] success! [/green]", file=sys.stderr)
        return True
    else:
        print("[red] alter failed! [/red]", file=sys.stderr)
        return False


"""
todo:
- db type in config
- models.py with db import or define_tables method.
- `public.` prefix
"""

"""
def pin:
pydal2sql pin 96de5b37b586e75b8ac053b9bef7647f544fe502  # -> default pin created
pydal2sql alter myfile.py # should compare between pin/@latest and @current
                          # replaces @current for Before, not for After in case of ALTER.
pydal2sql pin --remove # -> default pin removed

pydal2sql pin 96de5b37b586e75b8ac053b9bef7647f544fe502 --name my_custom_name # -> pin '@my_custom_name' created
pydal2sql pin 96de5b37b586e75b8ac053b9bef7647f544fe503 --name my_custom_name #-> pin '@my_custom_name' overwritten
pydal2sql create myfile.py@my_custom_name
pydal2sql pin 96de5b37b586e75b8ac053b9bef7647f544fe502 --remove -> pin '@my_custom_name' removed

pydal2sql pins
# lists hash with name
"""


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
    Todo: docs

    Args:
        _: context to determine if a subcommand is passed, etc
        config: path to a different config toml file
        verbosity: level of detail to print out (1 - 3)

        show_config: display current configuration?
        version: display current version?

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


# if __name__ == "__main__":
#     app()
